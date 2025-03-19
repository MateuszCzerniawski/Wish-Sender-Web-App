import os.path

import gpt_2_simple as gpt2
import tensorflow as tf
import re


def cleanup(text):
    parts = re.split('<\\|endoftext\\|>', text)
    if parts.__len__() > 1:
        text = parts[0]  # deleting unrelated text
    text = re.sub('\n\n.+\w$', '', text)  # chopping off unfinished sentences
    text = re.sub('\n\n', '\n', text)  # better new lines
    return text


class GPTcontroller:
    def __init__(self):
        tf.config.optimizer.set_experimental_options({"mlir_enabled": True})
        self.model_name = "355M"

    def generate(self, prefix):
        # nie podoba mi się konieczność każdorazowej inicjalizacji ale inaczej to nie działa
        sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(sess, model_name=self.model_name)
        text = gpt2.generate(sess, model_name=self.model_name, prefix=prefix, length=100, return_as_list=True)[0]
        gpt2.reset_session(sess)
        text = cleanup(text)
        return text


if not (os.path.exists('models/355M') and os.path.isdir('models/355M')):
    print(
        'GPT2 missing, need for download. This operation may cause critical runtime error or unwanted behavior!\nIn case of such, wait for download to complete and re-run the app')
    gpt2.download_gpt2(model_name='355M')
gpt = GPTcontroller()
