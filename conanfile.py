from conans import ConanFile, tools
from conans import VisualStudioBuildEnvironment, AutoToolsBuildEnvironment
from conans.util.files import load
from conans.errors import ConanException
import os
import sys


class QwtConan(ConanFile):
    name = "qwt"
    version = "6.1.5"
    license = "LGPL-3.0 with exceptions, http://qwt.sourceforge.net/qwtlicense.html"
    # Qwt License, Version 1.0
    opt_license ="LGPL-3.0"
    url = "https://github.com/sintef-ocean/conan-qwt"
    author = "Joakim Haugen (joakim.haugen@gmail.com)"
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
        "designer=True",
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

        qwt_build_string = "CONFIG += {}"\
            .format(("release" if self.settings.build_type == "Release" else "debug"))
        qwt_build_file_path = os.path.join(self.source_folder,
                                           self.qwt_path,
                                           "qwtbuild.pri")
        tools.replace_in_file(
            qwt_build_file_path, "CONFIG           += release",
            qwt_build_string)
        tools.replace_in_file(
            qwt_build_file_path, "CONFIG           += debug_and_release",
            qwt_build_string)
        tools.replace_in_file(
            qwt_build_file_path, "CONFIG           += build_all", "")

    def build(self):

        src_path = os.path.join(self.source_folder, self.qwt_path)
        self.run("qmake qwt.pro",
                 cwd=src_path,
                 run_environment=True)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    vcvars = tools.vcvars_command(self)
                    build_args = []
                    build_cmd = "jom"
                    self.run("{} && {} {}".format(vcvars,
                                                  build_cmd,
                                                  " ".join(build_args)),
                             cwd=src_path,
                             run_environment=True)
            else:
                raise ConanException("Not yet implemented for this compiler")
        else:
            self.run("make",
                     cwd=src_path,
                     run_environment=True)

    def package(self):
        self.copy("qwt*.h", dst="include",
                  src=os.path.join("qwt-{}".format(self.version),
                                   "src"))
        self.copy("*qwt.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses",
                  src=os.path.join(self.source_folder, self.qwt_path))

    def package_info(self):

        self.cpp_info.libs = ["qwt"]
        self.cpp_info.name = 'Qwt'