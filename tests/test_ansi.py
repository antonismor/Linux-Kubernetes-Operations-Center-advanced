import contextlib,io,os,unittest
from unittest.mock import patch
from lkoc.ansi import Screen,ANSI_RE,visible_len,pad
class AnsiTests(unittest.TestCase):
    def test_ansi_width(self):
        x='\033[38;5;46m● READY\033[0m';self.assertEqual(visible_len(x),len('● READY'));self.assertEqual(visible_len(pad(x,20)),20)
    def test_frame_alignment(self):
        out=io.StringIO()
        with patch('lkoc.ansi.shutil.get_terminal_size',return_value=os.terminal_size((120,40))):
            with contextlib.redirect_stdout(out):
                s=Screen();s.header(context='prod-cluster',version='1.0.0');s.section('NODES');s.section_row('k8s-worker-01 READY');s.section_row('very-long-node-name-that-must-not-break-the-right-border');s.section_end();s.footer()
        lines=[ANSI_RE.sub('',x) for x in out.getvalue().splitlines()]
        self.assertEqual({len(x) for x in lines},{120})
if __name__=='__main__':unittest.main()
