import re

text = "40k 15menit"
l_bl = ['opnn', '40k 15menit', 'testi vece 5detik🥰💋', 'opennnn.vcsss 25k', '40k 15menit', 'maaleeemmm horrrnnnyyy baangggeett sayaanggg ssssinii laaahhh aakuu teemeeeninnnnnn', 'maaleeemmm horrrnnnyyy baangggeett sayaanggg ssssinii laaahhh aakuu teemeeeninnn💋😡', '40k 15menit']

for word in l_bl:
    pattern = r"(|^|[^\w])" + re.escape(word) + r"(|$|[^\w])"
    if re.search(pattern, text, flags=re.IGNORECASE):
        print(word, "match")
    else:
        print(word, "not match")