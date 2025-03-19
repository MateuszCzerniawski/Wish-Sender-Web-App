from DataLoader import wishes, wish_tweaks


def print_tweaks(category):
    replacements = ['Father']
    for file in wish_tweaks[category]:
        print(file + ": ")
        print(get_wish(category,file,replacements=replacements))


def fill_gaps(gaps, replacements, text):
    if gaps.__len__() > replacements.__len__():
        return text
    for i in range(gaps.__len__()):
        text = text.replace(gaps[i], replacements[i])
    return text


def get_wish(category, filename, replacements=None):
    if replacements is None:
        replacements = list()
    return fill_gaps(wish_tweaks[category][filename], replacements, wishes[category][filename])

