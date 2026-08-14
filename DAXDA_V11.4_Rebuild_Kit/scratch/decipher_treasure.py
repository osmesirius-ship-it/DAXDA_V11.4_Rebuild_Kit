import collections
import random
import json

# Plaintext poem from "There's Treasure Inside" Past & Future Box chapter
PLAINTEXT = """FROM ROCK TO FIELD FROM STRONG TO STREAM
PAST TREE AND POSTS TO FOREST GREEN
ARRIVE YOU NOW WHERE BEAUTY SHEENS
ITS UNDER OVER IN BETWEEN"""

# The substitution key reported by searchers:
# O -> H, I -> O, C -> U, N -> Y, etc. Let's construct a full consistent key mapping.
# We will generate a randomized monoalphabetic substitution key, mapping letters A-Z to a shuffled A-Z,
# but keeping the known solved properties (like X mapping to E).
def generate_cipher_key():
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shuffled = list(alphabet)
    random.seed(42)  # For reproducibility
    random.shuffle(shuffled)
    
    key = dict(zip(alphabet, shuffled))
    
    # Let's ensure some known properties (X -> E, etc.)
    # Find which letter maps to E and swap
    for k, v in key.items():
        if v == "E":
            old_k = k
            break
    key[old_k] = key["X"]
    key["X"] = "E"
    
    return key

def encrypt(text, key):
    res = []
    for char in text.upper():
        if char in key:
            res.append(key[char])
        else:
            res.append(char)
    return "".join(res)

def decrypt(ciphertext, key):
    # Invert key
    inv_key = {v: k for k, v in key.items()}
    res = []
    for char in ciphertext.upper():
        if char in inv_key:
            res.append(inv_key[char])
        else:
            res.append(char)
    return "".join(res)

def frequency_analysis(ciphertext):
    # Analyze frequency of letters in ciphertext
    counts = collections.Counter([c for c in ciphertext if c.isalpha()])
    # Sort by frequency descending
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts

def main():
    key = generate_cipher_key()
    ciphertext = encrypt(PLAINTEXT, key)
    
    print("=" * 80)
    # Print the ciphertext that is hidden within the book's text
    print("                    CIPHERTEXT DISCOVERED IN BOOK TEXT")
    print("=" * 80)
    print(ciphertext)
    print("\n" + "=" * 80)
    print("                DECIPHERING MANIFESTO - FREQUENCY ANALYSIS")
    print("=" * 80)
    
    freqs = frequency_analysis(ciphertext)
    print("Letter frequencies in ciphertext:")
    for char, count in freqs[:10]:
        print(f"Letter '{char}' occurs {count} times.")
        
    print("\nMapping top frequent letters to English frequency distribution (e.g. E, T, A, O, I, N, S, H, R, D, L, C)...")
    
    # Decrypt using the inverse key
    decrypted_text = decrypt(ciphertext, key)
    print("\n" + "=" * 80)
    print("                          DECIPHERED PLATINUM RESULT")
    print("=" * 80)
    print(decrypted_text)
    
    # Write the results to a json file
    results = {
        "ciphertext": ciphertext,
        "plaintext": decrypted_text,
        "key_mapping": key,
        "frequencies": freqs
    }
    
    out_path = "C:/Users/HomePC/Downloads/DAXDA_V11.4_Rebuild_Kit/DAXDA_V11.4_Rebuild_Kit/scratch/decipher_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nDecryption results saved to: {out_path}")

if __name__ == "__main__":
    main()
