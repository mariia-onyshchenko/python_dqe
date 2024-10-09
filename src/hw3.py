
class Task3():
    def txt():
        text = """tHis iz your homeWork, copy these Text to variable.


You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.


it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.


last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""


        text = text.lower().replace(" iz ", " is ").replace(" iz.", " is.").replace(" iz,", " is,")
        last_words = [sentence.split()[-1] for sentence in text.rstrip('.').split('. ')]
        new_sent = ' '.join(last_words)
        text += ' ' + new_sent
        ws_count = sum(1 for char in text if char.isspace())
        fin_text = " ".join(text.split())
        fin_text = " ".join(s.capitalize()+'.' for s in fin_text.split('. '))

        return f'normalized text:\n{fin_text} \nnumber of white space chars:{ws_count}'
Task3.txt()
