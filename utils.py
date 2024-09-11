import random
import string

def generate_random_string(*, string_length=10) -> str:
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(string_length))
