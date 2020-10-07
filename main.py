from aiohttp import web
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import random
import json

with open('quotes.json', 'r') as f:
	quotes = json.loads(f.read())

routes = web.RouteTableDef()

font = ImageFont.truetype('Georgia.ttf', 48)

def wrap_text(text, line_length):
	output = ''
	current_line_length = 0
	
	for word in text.split(' '):
		word = word + ' '
		word_length = font.getsize(word)[0]
		new_line_length = current_line_length + word_length
		if '\n' in word:
			current_line_length = 0
		print(word_length)
		while word_length > line_length:
			output += word[:30] + '\n'
			word = word[30:]
			word_length = font.getsize(word)[0]
			print('word is too long!')
		if new_line_length > line_length:
			output = output.strip()
			output += '\n'
			current_line_length = 0
			print('wrapped because length overflowed')
		current_line_length += font.getsize(word)[0]
		output += word.lstrip(' ')
	return output.strip()

async def create_quote_image(quote=None):
	im = Image.open('suntzu.jpg')

	if quote is None:
		quote = 'Sample Text'
	quote = wrap_text(quote, 18 * 48)
	print(quote)
	italic_text = '- Sun Tzu, The Art of War'

	draw = ImageDraw.Draw(im)
	quote_height = font.getsize(quote)[1]
	draw.text((400, 290 - quote.count('\n') * 24), quote, (255, 255, 255), font=font)
	draw.text((500, 350 + quote.count('\n') * 24), italic_text, (255, 255, 255), font=font)

	with BytesIO() as output:
		im.save(output, format='png')
		contents = output.getvalue()
	return contents

@routes.get('/quote.png')
async def generate_quote_png(request):
	contents = await create_quote_image(request.query.get('quote'))
	return web.Response(body=contents, content_type='image/png')

@routes.get('/random')
async def random_quote(request):
	quote = random.choice(quotes)['text']
	return web.HTTPFound('/quote.png?quote=' + quote)

app = web.Application()
app.add_routes(routes)
web.run_app(app)