from conans import ConanFile, tools
from conans import VisualStudioBuildEnvironment, AutoToolsBuildEnvironment
from conans.util.files import load
from conans.errors import ConanException
import os
import sys
import shutil


class QwtConan(ConanFile):
    name = "qwt"
    version = "6.1.5"
    license = "LGPL-3.0 with exceptions, http://qwt.sourceforge.net/qwtlicense.html"
    # Qwt License, Version 1.0
    opt_license ="LGPL-3.0"
    url = "https://github.com/sintef-ocean/conan-qwt"
    author = "SINTEF Ocean"
    homepage = "https://qwt.sourceforge.io"
    description = \
        "The Qwt library contains GUI Components and utility classes which are "\
        "primarily useful for programs with a technical background. Beside a " \
        "framework for 2D plots it provides scales, sliders, dials, compasses, "\
        "thermometers, wheels and knobs to control or display values, arrays, " \
        "or ranges of type double."
    topics = ("visualization", "plotting", "qwt", "qt")
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "plot": [True, False],
        "widgets": [True, False],
        "svg": [True, False],
        "opengl": [True, False],
        "mathml": [True, False],
        "designer": [True, False],
        "examples": [True, False],
        "playground": [True, False]
    }

    default_options = (
        "shared=True",
        "plot=True",
        "widgets=True",
        "svg=True",
        "opengl=True",
        "mathml=False",
        "designer=False",
        "examples=False",
        "playground=False")

    generators = ("cmake")

    qwt_path = "qwt-{}".format(version)

    def requirements(self):
        self.requires("qt/5.15.0@bincrafters/stable")

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler == "Visual Studio":
            self.build_requires("jom/1.1.3")

    def configure(self):

        self.options["qt"].qtsvg = self.options.svg

    def source(self):

        url_base = "https://sourceforge.net/projects/qwt/files/qwt/{ver}/qwt-{ver}"\
            .format(ver=self.version)
        if self.settings.os != "Windows":
            url = "{}{}".format(url_base, ".tar.bz2")
            tools.get(url, sha1="07c71427f1f4bbd0354b3a98965943ce2f220766")
        else:
            url = "{}{}".format(url_base, ".zip")
            tools.get(url, sha1="98ab9cd566df9fc8f049dc0aa780d2d8ebe08cde")

        src_path = os.path.join(self.source_folder, self.qwt_path)
        os.rename(os.path.join(src_path, 'COPYING'),
                  os.path.join(src_path, 'LICENSE'))

        qwt_config_file_path = os.path.join(self.source_folder,
                                            self.qwt_path,
                                            "qwtconfig.pri")
        qwt_config = load(qwt_config_file_path)
        qwt_config += "\nQWT_CONFIG {}= QwtDLL"\
            .format(("+" if self.options.shared else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtPlot"\
            .format(("+" if self.options.plot else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtWidgets"\
            .format(("+" if self.options.widgets else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtSvg"\
            .format(("+" if self.options.svg else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtOpenGL"\
            .format(("+" if self.options.opengl else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtMathML"\
            .format(("+" if self.options.mathml else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtDesigner"\
            .format(("+" if self.options.designer else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtExamples"\
            .format(("+" if self.options.examples else "-"))
        qwt_config += "\nQWT_CONFIG {}= QwtPlayground"\
            .format(("+" if self.options.playground else "-"))
        qwt_config = qwt_config.encode("utf-8")
        with open(qwt_config_file_path, "wb") as handle:
            handle.write(qwt_config)

        qwt_build_path = os.path.join(self.source_folder,
                                      self.qwt_path)

        os.rename(os.path.join(qwt_build_path, 'qwtbuild.pri'),
                  os.path.join(qwt_build_path, 'qwtbuild.tmpl'))

    def build(self):

        qwt_build_string = "CONFIG += {}"\
            .format(("release" if self.settings.build_type == "Release" else "debug"))
        qwt_build_file_path = os.path.join(self.source_folder,
                                           self.qwt_path,
                                           'qwtbuild.{}')
        shutil.copy(qwt_build_file_path.format('tmpl'),
                    qwt_build_file_path.format('pri'))

        tools.replace_in_file(
            qwt_build_file_path.format('pri'),
            "CONFIG           += release",
            qwt_build_string)
        tools.replace_in_file(
            qwt_build_file_path.format('pri'),
            "CONFIG           += debug_and_release",
            qwt_build_string)
        tools.replace_in_file(
            qwt_build_file_path.format('pri'),
            "CONFIG           += build_all", "")

        if self.settings.compiler == 'clang':
            qwt_build = load(qwt_build_file_path.format('pri'))
            qwt_build += "\nQMAKE_CC=clang-{}"\
                .format(self.settings.compiler.version)
            qwt_build += "\nQMAKE_LINK_C=clang-{}"\
                .format(self.settings.compiler.version)
            qwt_build += "\nQMAKE_LINK_C_SHLIB=clang-{}"\
                .format(self.settings.compiler.version)
            qwt_build += "\nQMAKE_CXX=clang++-{}"\
                .format(self.settings.compiler.version)
            qwt_build += "\nQMAKE_LINK=clang++-{}"\
                .format(self.settings.compiler.version)
            qwt_build += "\nQMAKE_LINK_SHLIB=clang++-{}"\
                .format(self.settings.compiler.version)
            qwt_build = qwt_build.encode("utf-8")
            with open(qwt_build_file_path.format('pri'), "wb") as handle:
                handle.write(qwt_build)

        src_path = os.path.join(self.source_folder, self.qwt_path)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self.settings):
                    self.run("qmake qwt.pro",
                             cwd=src_path,
                             run_environment=True)
                    self.run("jom",
                             cwd=src_path,
                             run_environment=True)
            else:
                raise ConanException("Unsupported settings, recipe not implemented")
        else:
            self.run("qmake qwt.pro",
                     cwd=src_path,
                     run_environment=True)
            self.run("make",
                     cwd=src_path,
                     run_environment=True)

    def package(self):
        self.copy("qwt*.h", dst="include",
                  src=os.path.join("qwt-{}".format(self.version),
                                   "src"))
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.pdb", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses",
                  src=os.path.join(self.source_folder, self.qwt_path))

    def package_info(self):

        self.cpp_info.libs = ["qwt"]
        if self.settings.build_type == "Debug"\
           and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs[0] += 'd'
        self.cpp_info.name = 'Qwt'
