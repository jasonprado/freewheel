""" Requires PIL (or, preferably pillow) with jpeg extensions"""

from PIL import Image
import random, string
import itertools, collections, operator

IMG_WIDTH = 320
IMG_HEIGHT = 320


def get_image_and_pixel_map(filename):
    img = Image.open(filename)
    rgb = img.convert('RGB')
    pixels = rgb.load()
    return (rgb, pixels)

def make_bits():
    return ''.join(random.choice(string.printable) for i in range(1024 * 10 - 1));


Pixel = collections.namedtuple('Pixel', ['x', 'y', 'r', 'g', 'b'])


class Mapper(object):
    def char_to_pixels(self, char, index):
        """ returns a list of `Pixel`s """
        raise NotImplementedError

    def map(self, data, pixel_map):
        out_pixels = [self.char_to_pixels(char, i) for (i, char) in enumerate(data)]
        chain = itertools.chain.from_iterable(out_pixels)
        for p in chain:
            pixel_map[p.x, p.y] = (p.r, p.g, p.b)

    def read(self, pixel_map, data_len):
        raise NotImplementedError


class OnesquareMapper(Mapper):
    def char_to_pixels(self, char, index):
        x = index % IMG_WIDTH
        y = index / IMG_WIDTH
        val = ord(char)
        return [Pixel(x=x, y=y, r=val, g=val, b=val)]

    def read(self, pixel_map, data_len):
        positions = [(i % IMG_WIDTH, i / IMG_WIDTH) for i in range(data_len)]
        out_data = []
        for (x, y) in positions:
            (r, g, b) = pixel_map[x, y]
            val = (r + g + b)/3  # just average them?
            char = chr(val)
            out_data.append(char)

        return out_data


class Bands(object):
    # min, max, val
    bands = [(0, 42, 0),
    (42 + 1, 42*3, 42*2),
    (42*3 + 1, 42*5, 42*4),
    (42*5 + 1, 255, 255)]

    @classmethod
    def two_bits_to_band_val(cls, two_bits):
        return cls.bands[two_bits][2]

    @classmethod
    def value_to_two_bits(cls, value):
        for i, band in enumerate(cls.bands):
            if band[0] <= value <= band[1]:
                return i
        return None

    @classmethod
    def best_match(cls, list_of_vals):
        ideal_band_vals = [band[2] for band in cls.bands]
        pairs = itertools.product(list_of_vals, ideal_band_vals)
        diffs = [(ideal, abs(val - ideal)) for (val, ideal) in pairs]
        min_diff = min(diffs, key=operator.itemgetter(1))
        best_match = min_diff[0]
        return best_match


class FoursquareMapper(Mapper):

    def val_to_bands(self, val):
        # val is a byte-sized val
        band_values = []
        for i in range(4):
            bits = val % 4
            band_values.append(Bands.two_bits_to_band_val(bits))
            val = val / 4
        return band_values

    def char_to_pixels(self, char, index):
        x = (index * 2) % IMG_WIDTH
        xs = [x, x+1]
        y = ((index * 2) / IMG_WIDTH) * 2
        ys = [y, y+1]
        positions = itertools.product(xs, ys)
        val = ord(char)
        band_values = self.val_to_bands(val)
        band_values *= 3

        pixels = [
            Pixel(x=x, y=y,
                  r=band_values[0 + 3*i],
                  g=band_values[1 + 3*i],
                  b=band_values[2 + 3*i])
            for i, (x, y) in enumerate(positions)]

        return pixels

    def read(self, pixel_map, data_len):
        positions = [(i*2 % IMG_WIDTH, (i*2 / IMG_WIDTH) * 2 ) for i in range(data_len)]
        out_data = []
        for p in positions:
            xs = [p[0], p[0] + 1]
            ys = [p[1], p[1] + 1]
            square = itertools.product(xs, ys)
            total = 0
            band_vals = []
            for i, (x, y) in enumerate(square):
                for band_val in pixel_map[x, y]:
                    band_vals.append(band_val)

            chunked = [band_vals[i:i+4] for i in xrange(0, len(band_vals), 4)]
            zipped = zip(*chunked)
            best_matches = map(Bands.best_match, zipped)
            two_bit_vals = [Bands.value_to_two_bits(band_val) for band_val in best_matches]
            acc = 0
            for val in two_bit_vals:
                acc *= 4
                acc += val
            char = chr(acc)
            out_data.append(char)

        return out_data

class BlackAndWhiteMapper(Mapper):
    def char_to_pixels(self, char, index):
        val = ord(char)
        bit_string = '{0:08b}'.format(val)
        pixels = []
        for i, bit in enumerate(bit_string):
            x = ((index * 8) + i) % IMG_WIDTH
            y = ((index * 8) + i) / IMG_WIDTH
            pixel_val = 255 if int(bit) else 0
            p = Pixel(x=x, y=y, r=pixel_val, g=pixel_val, b=pixel_val)
            pixels.append(p)
        return pixels

    def read(self, pixel_map, data_len):
        positions = [(i % IMG_WIDTH, i / IMG_WIDTH) for i in range(data_len * 8)]
        chunked = [positions[i:i+8] for i in xrange(0, data_len * 8, 8)]
        out_data = []
        for eight_chunk in chunked:
            pixel_vals = [pixel_map[position] for position in eight_chunk]
            sums = map(sum, pixel_vals)
            bools = map(lambda x: x > (255 * 3)/2, sums)
            bits = map(int, bools)
            val = reduce(lambda acc, bit: (acc * 2 + bit), bits, 0)

            char = chr(val)
            out_data.append(char)

        return out_data


img, pixel_map = get_image_and_pixel_map('the_joy_of_youth.jpg')
data = make_bits()

m = BlackAndWhiteMapper()
m.map(data, pixel_map)

img.save('the_pain_of_youth.jpg', 'jpeg')
out_img, out_pixel_map = get_image_and_pixel_map('the_pain_of_youth.jpg')

out_data = m.read(out_pixel_map, len(data))

hits, misses = 0, 0
for i in range(len(data)):
    if data[i] == out_data[i]:
        hits += 1
    else:
        misses += 1

print "hits", hits, "misses", misses
print "hit rate: %s" % (float(hits) / (hits + misses))

difference_image = out_img.copy()
difference_map = difference_image.load()

max_diff = 0
for x in range(IMG_WIDTH):
    for y in range(IMG_HEIGHT):
        (r1, g1, b1) = difference_map[x, y]
        (r2, g2, b2) = pixel_map[x, y]
        diff = ((r1-r2), (g1-g2), (b1-b2))
        max_diff = max(max_diff, max(diff))
        difference_map[x, y] = diff
print "max diff was: %s" % max_diff

difference_image.save("difference_map.png", "png")
