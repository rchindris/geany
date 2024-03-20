"""Prompt for joint intent and slot sample generation."""

import re
import logging

from typing import Dict, List
from jinja2 import Template

from hyperconf import hypermap, HyperConfig
from geany.abc import Prompt, PromptBuilder


@hypermap("intent_prompt")
class IntentPromptBuilder(PromptBuilder):
    
    def get_prompts(self, config: HyperConfig | Dict):
        """Create intent prompts.

        This builer creates one prompt for each intent definition.
        Given a definition.
        
        Args:
        config (HyperConfig | Dict): prompt configuration. Must be a
        HyperConfig object or a dict containing the context for the
        prompt template.
        """
        if config is None:
            raise ValueError("config is None")

        return [
            IntentWithSlotPrompt(
                config.domain_spec,
                intent_tag = i.tag,
                intent_desc = i.description,
                slots = i.slots,
                examples = i.examples
            ) for i in config.intents
        ]

        
class IntentWithSlotPrompt(Prompt):
    """Prompt for generating intent and slot samples.

    This prompt follows the prompt guidelines from:
    Sharma et al. (2023), Augmenting Text for Spoken Language Understanding
    with Large Language Models.
    """

    _PROMPT_TEMPLATE = """
You are working in an intent-and-slot framework where every utterance can
be classified under an intent. {{domain_desc}}
Your task is to generate samples for intents. Each sample should be
enclosed in square brackets [ ]. The first square bracket [ should be followed by
an intent tag that is in uppercase letters and begins with I_.
Inside the sentence, you should label some nouns with slot tags, which are also enclosed
in brackets [ ]. Slot tags are in all uppercase letters and begin with SL_.
In each sentence, there can only be 1 intent, but there can be many slots.
{% if intent_desc %}
The intent {{ intent_tag }} means that the human {{ intent_desc }}.
{% else %}
The intent tag is {{ intent_tag }}.
{% endif %}
{% if slots %}
It can contain the following slot types: {{ slots|join(", ") }}.
{% endif %}
Some examples for this intent are:
{% for ex in examples %}
[{{ intent_tag }} {{ ex }} ]
{% endfor %}
    """
    def __init__(self, domain_desc: str, intent_tag: str,
                 intent_desc: str, slots: List[str], examples: List[str]):
        """Initialize for specified intents and slot specs.

        Args:
        domain_desc (str): a description of the environment in which the
          bot operates.
        intent_tag (str): a label tag for the intent.
        intent_desc (str): the action that the bot should perform for this intent.
        This is a descriptive text, it provides the context for this intent to the LLM.
        slots (List[str]): a list containing slot tags.
        examples (List[str]): a list containing utterance examples with annotated slots.
        """
        
        if domain_desc is None:
            raise ValueError("domain_desc is None")
        if intent_tag is None:
            raise ValueError("intent_tag is None")
        self._intent_tag = intent_tag
        self._context = {
            "domain_desc": domain_desc,
            "intent_tag": intent_tag,
            "intent_desc": intent_desc,
            "slots": slots,
            "examples": examples
        }
        self._template = Template(IntentWithSlotPrompt._PROMPT_TEMPLATE)
        
        self._re_int = re.compile(r"\[\s*(I_[A-Z_]+)(.*)\]")
        self._re_slot = re.compile(r"\[\s*(SL_[A-Z]+)\s+([^\]]+)\]")

    def get_context(self):
        return self._template.render(self._context)

    def get_instruction(self, num_samples: int):
        return f"Generate {num_samples} utterances for intent {self._intent_tag}."\
            " Try not to repeat utterances."

    def parse_output(self, text: str):
        """Extract annotated samples from the output.

        The `text` is the raw output from the LLM, it contains lines
        formatted as =[I_INTENT token token ... [SL_SLOT slot ...]...]=.
        This function parses each line and returns a dictionary containing:
        intents - a list of intent labels, one for each line
        text - the raw utterance text, with annotations removed.
        slots - a string containing slot labels and the special `O` label.
        """
        if text is None:
            raise ValueError("text is None")

        samples = {
            "intent": [],
            "text": [],
            "slots": []
        }
        
        lines = [line.strip() for line in text.split("\n")]
        for line in lines:
            intent_match = self._re_int.match(line)
            if not intent_match:
                logging.error(f"incorrect sample: {line}")
                continue
            
            tokens = []
            slot_labels = []
            sub_pos = 0
            
            intent = intent_match.group(1)
            utterance = intent_match.group(2)
            
            for m in  self._re_slot.finditer(utterance):
                new_tokens = [x for x in utterance[sub_pos: m.start()].split(" ") if len(x)]
    
                tokens.extend(new_tokens)
                slot_labels.extend(['O'] * len(new_tokens))

                slot_label = m.group(1)
                slot_tokens = [x for x in m.group(2).split(" ") if len(x)]

                tokens.extend(slot_tokens)
                slot_labels.extend([slot_label] * len(slot_tokens))

                sub_pos = m.end() + 1

            samples["intent"].append(intent)
            samples["text"].append(" ".join(tokens))
            samples["slots"].append(" ".join(slot_labels))

        return samples

                
                
        
    
    
    
