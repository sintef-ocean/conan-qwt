#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake
import os


class QwtTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    default_options = "qwt:designer=False"
    generators = ("cmake_paths", "cmake_find_package")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst=str(self.settings.build_type), keep_path=False)

    def test(self):
        program = 'example'
        if self.settings.os == "Windows":
            program += '.exe'
            test_path = os.path.join(str(self.build_folder),
                                     str(self.settings.build_type))
        else:
            test_path = '.' + os.sep
        self.run(os.path.join(test_path, program + " -platform offscreen"))
