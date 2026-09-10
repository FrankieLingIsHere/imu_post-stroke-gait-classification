"""Exercise interrupted transfers against a real local HTTP server."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
import requests

from src.data.http_ranges import download_range

PAYLOAD = bytes(range(256))*1024


class RangeTransferTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        log = self.requests
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_GET(self):
                start,end=map(int,self.headers['Range'].removeprefix('bytes=').split('-'))
                log.append((start,end))
                if self.path=='/ignore':
                    self.send_response(200);self.end_headers();return
                self.send_response(206)
                self.send_header('Content-Range',f'bytes {start}-{end}/{len(PAYLOAD)}')
                self.send_header('Content-Length',str(end-start+1))
                self.send_header('ETag','"test-v1"')
                self.end_headers()
                if self.path=='/interrupt' and len(log)==1:
                    self.wfile.write(PAYLOAD[start:start+70000]);self.wfile.flush()
                    self.close_connection=True
                else:self.wfile.write(PAYLOAD[start:end+1])
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
        self.temp=tempfile.TemporaryDirectory()

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
        self.temp.cleanup()

    def test_resume_after_truncated_body_and_reuse_completed_cache(self):
        data=download_range(self.url+'/interrupt',0,len(PAYLOAD)-1,self.temp.name,backoff=0)
        self.assertEqual(data,PAYLOAD)
        self.assertEqual(self.requests[1][0],65536)
        self.assertEqual(download_range(self.url+'/interrupt',0,len(PAYLOAD)-1,self.temp.name),PAYLOAD)
        self.assertEqual(len(self.requests),2)

    def test_ignored_range_does_not_download_full_archive(self):
        with self.assertRaisesRegex(ValueError,'HTTP 200'):
            download_range(self.url+'/ignore',0,99,self.temp.name)
        self.assertEqual(list(Path(self.temp.name).glob('*.part')),[])

    def test_resume_in_a_later_invocation(self):
        with self.assertRaises(requests.exceptions.ChunkedEncodingError):
            download_range(self.url+'/interrupt',0,len(PAYLOAD)-1,self.temp.name,attempts=1)
        self.assertEqual(next(Path(self.temp.name).glob('*.part')).stat().st_size,65536)
        self.assertEqual(download_range(self.url+'/interrupt',0,len(PAYLOAD)-1,self.temp.name),PAYLOAD)
        self.assertEqual(self.requests[1][0],65536)

    def test_detects_corrupt_complete_cache(self):
        url=self.url+'/ok'
        download_range(url,0,99,self.temp.name)
        cache=Path(self.temp.name)/hashlib.sha256(f'{url}:0:99'.encode()).hexdigest()
        cache.write_bytes(b'x'*100)
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):
            download_range(url,0,99,self.temp.name)


if __name__=='__main__': unittest.main()
