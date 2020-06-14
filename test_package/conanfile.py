#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment
import os


class QwtTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ("qt", "cmake", "cmake_paths", "cmake_find_package")
    requires = "harfbuzz/[>=2.6.7]@bincrafters/stable"

    def build(self):
        env_build = RunEnvironment(self)
        with tools.environment_append(env_build.vars):
            cmake = CMake(self, set_cmake_flags=True)
            cmake.configure()
            cmake.build()

    def test(self):
        program = 'example'
        if self.settings.os == "Windows":
            program += '.exe'
            test_path = os.path.join(str(self.build_folder),
                                     str(self.settings.build_type))
        else:
            test_path = '.' + os.sep
        self.run(os.path.join(test_path, program + " -platform offscreen"),
                 run_environment=True)
