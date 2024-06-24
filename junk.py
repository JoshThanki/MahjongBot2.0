print(len(bin(24007)[2:]))


Base = 47
value = ((Base / 9) * 7 + Base % 9) * 3

print(value)


def encode_chi(base, chi, tiles, who, called):
    # Base Tile and Called Tile calculation
    base_tile_and_called_tile = ((base // 9) * 7 + base % 9) * 3 + chi
    
    # T[0-2] calculation
    T = [(tiles[i] - 4 * i - base * 4) for i in range(3)]
    
    # Construct the 16-bit binary representation
    # base_tile_and_called_tile takes the first 7 bits
    # T[2], T[1], T[0] each take 3 bits
    # Who takes 2 bits
    chi_bits = (base_tile_and_called_tile << 9) | (T[2] << 6) | (T[1] << 3) | T[0]
    chi_bits = (chi_bits << 2) | who
    chi_bits = (chi_bits << 1) | called
    
    # Ensure the result fits into a 16-bit unsigned integer
    chi_bits = chi_bits & 0xFFFF
    
    # Return the 16-bit integer value
    return chi_bits

# Example values
base = 47       # The lowest tile in the chi / 4
chi = 1           # Chi type (e.g., 0: left, 1: middle, 2: right)
tiles = [12, 16, 20]  # The tiles in the chi
who = 1           # Offset of player the tile was called from
called = 47        # Which tile out of the three was called

encoded_chi = encode_chi(base, chi, tiles, who, called)
print(encoded_chi)  # Output the 16-bit integer representation in base 10

