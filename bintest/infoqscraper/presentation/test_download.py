# -*- coding: utf-8 -*-
#
# Copyright (c) 2012, Clément MATHIEU
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import shutil
import subprocess
import sys
import tempfile

from bintest.infoqscraper import TestInfoqscraper

usage_prefix = "usage: infoqscraper presentation"

# Shorter is better to speed up the test suite.
short_presentation_id = "Batmanjs"  # 25 minutes


class TestArguments(TestInfoqscraper):

    def setUp(self):
        self.default_cmd = ["-c", "presentation", "download"]

    def test_help(self):
        output = self.run_cmd(self.default_cmd + ["--help"])
        self.assertTrue(output.startswith(usage_prefix))

    def test_no_arg(self):
        try:
            self.run_cmd(self.default_cmd)
            self.fail("Exception expected")
        except subprocess.CalledProcessError as e:
            self.assertEqual(e.returncode, 2)
            self.assertTrue(e.output.decode('utf8').startswith(usage_prefix))

    def test_download_h264(self):
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "output.avi")
        self.run_cmd(self.default_cmd + [short_presentation_id, "-o", output_path, "-t", "h264"])
        self.assertTrue(os.path.exists(output_path))
        shutil.rmtree(tmp_dir)

    def test_download_h264_overlay(self):
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "output.avi")
        self.run_cmd(self.default_cmd + [short_presentation_id, "-o", output_path, "-t", "h264_overlay"])
        self.assertTrue(os.path.exists(output_path))
        shutil.rmtree(tmp_dir)

    def test_download_url(self):
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "output.avi")
        url = "http://www.infoq.com/presentations/" + short_presentation_id
        self.run_cmd(self.default_cmd + [url, "-o", output_path])
        self.assertTrue(os.path.exists(output_path))
        shutil.rmtree(tmp_dir)

    def test_download_output_file_already_exist(self):
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "output.avi")
        open(output_path, 'w').close()
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            self.run_cmd(self.default_cmd + [short_presentation_id, "-o", output_path])
        self.assertEquals(cm.exception.returncode, 2)
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(os.stat(output_path).st_size == 0)
        shutil.rmtree(tmp_dir)

    def test_download_overwrite_output_file(self):
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "output.avi")
        open(output_path, 'w').close()
        self.run_cmd(self.default_cmd + [short_presentation_id, "-o", output_path, "-y"])
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(os.stat(output_path).st_size > 0)
        shutil.rmtree(tmp_dir)

    def assert_bad_command(self, args):
        try:
            self.run_cmd(self.default_cmd + args)
            self.fail("Exception expected")
        except subprocess.CalledProcessError as e:
            self.assertEqual(e.returncode, 2)
            self.assertTrue(e.output.decode('utf8').startswith(usage_prefix))

    def test_bad_ffmpeg(self):
        self.assert_bad_command(["--ffmpeg", "/bad/ffmpeg/path"])

    def test_bad_swfrender(self):
        self.assert_bad_command(["--swfrender", "/bad/swfrender/path"])

    def test_bad_rtmpdump(self):
        self.assert_bad_command(["--rtmpdump", "/bad/rtmpdump/path"])

    def test_custom_ffmpeg(self):
        if sys.platform.startswith("win32"):
            # TODO: Need to find a way to create an alias on win32
            return

        ffmpeg_path = subprocess.check_output(["which", "ffmpeg"]).strip()
        tmp_dir = tempfile.mkdtemp()
        try:
            alias_path = os.path.join(tmp_dir, "ffmpeg")
            print(ffmpeg_path)
            os.symlink(ffmpeg_path, alias_path)

            output_path = os.path.join(tmp_dir, "output.avi")
            self.run_cmd(self.default_cmd + [short_presentation_id, "-o", output_path])
            self.assertTrue(os.path.exists(output_path))
        finally:
            shutil.rmtree(tmp_dir)
