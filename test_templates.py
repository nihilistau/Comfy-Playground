import tempfile
import os
from src import templates

def test_get_and_save_templates(tmp_path):
    os.environ['DRIVE_ROOT'] = str(tmp_path)
    # ensure defaults created
    t = templates.get_prompt_templates()
    assert isinstance(t, list)
    # save new templates
    new = [{"name":"A","template":"A {prompt}"}]
    templates.save_prompt_templates(new)
    t2 = templates.get_prompt_templates()
    assert t2[0]['name'] == 'A'
