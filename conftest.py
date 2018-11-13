"""
Copyright (c) 2018, Michael Pinkert
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Laboratory for Optical and Computational Instrumentation nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import imagej
import pytest

def pytest_addoption(parser):
        parser.addoption(
                "--ij", action="store", default="/Applications/Fiji.app", help="directory to IJ"
        )
        parser.addoption(
                "--headless", action="store", default='True', help="Start in headless mode"
        )


@pytest.fixture(scope='session')
def ij(request):
        ij_dir = request.config.getoption('--ij')
        headless = bool(request.config.getoption('--headless'))
        ij_wrapper = imagej.init(ij_dir)

        # General-purpose utility methods.

        import jnius

        # -- Python to Java --

        from collections import Iterable, Mapping, Set

        # Adapted from code posted by vslotman on GitHub:
        # https://github.com/kivy/pyjnius/issues/217#issue-145981070

        jDouble = jnius.autoclass('java.lang.Double')
        jFloat = jnius.autoclass('java.lang.Float')
        jInteger = jnius.autoclass('java.lang.Integer')
        jLong = jnius.autoclass('java.lang.Long')
        jString = jnius.autoclass('java.lang.String')
        jBigDecimal = jnius.autoclass('java.math.BigDecimal')
        jBigInteger = jnius.autoclass('java.math.BigInteger')
        jArrayList = jnius.autoclass('java.util.ArrayList')
        jLinkedHashMap = jnius.autoclass('java.util.LinkedHashMap')
        jLinkedHashSet = jnius.autoclass('java.util.LinkedHashSet')
        jBool = jnius.autoclass('java.lang.Boolean')

        class JavaNumber(object):
                '''
                Convert int/float to their corresponding Java-types based on size
                '''

                def __call__(self, obj):
                        if isinstance(obj, int):
                                if obj <= jInteger.MAX_VALUE:
                                        return jInteger(obj)
                                elif obj <= jLong.MAX_VALUE:
                                        return jLong(obj)
                                else:
                                        return jBigInteger(str(obj))
                        elif isinstance(obj, float):
                                if obj <= jFloat.MAX_VALUE:
                                        return jFloat(obj)
                                elif obj <= jDouble.MAX_VALUE:
                                        return jDouble(obj)
                                else:
                                        return jBigDecimal(str(obj))

        class JavaString(object):
                '''
                Convert str to Java equivalent, with default encoding of UTF-8
                '''
                
                def __call__(self, obj, encoding='utf-8'):
                        return jString(obj.encode(encoding), encoding)

        def to_java(data):
                '''
                Recursively convert Python object to Java object
                :param data:
                '''
                java_type_map = {
                        int: JavaNumber(),
                        str: JavaString(),
                        float: JavaNumber(),
                        bool: jBool
                }
                if type(data) in java_type_map:
                        # We know of a way to convert type.
                        return java_type_map[type(data)](data)
                elif isinstance(data, jnius.MetaJavaClass):
                        # It's already a Java object.
                        return data
                elif isinstance(data, Mapping):
                        # Object is dict-like.
                        jmap = jLinkedHashMap()
                        for k, v in data.items():
                                jk = to_java(k)
                                jv = to_java(v)
                                jmap.put(jk, jv)
                        return jmap
                elif isinstance(data, Set):
                        # Object is set-like.
                        jset = jLinkedHashSet()
                        for item in data:
                                jitem = to_java(item)
                                jset.add(jitem)
                        return jset
                elif isinstance(data, Iterable):
                        # Object is list-like.
                        jlist = jArrayList()
                        for item in data:
                                jitem = to_java(item)
                                jlist.add(jitem)
                        return jlist
                else:
                        raise TypeError('Unsupported type: ' + str(type(data)))

        # -- Java to Python --

        jIterableClass = jnius.find_javaclass('java.lang.Iterable')
        jCollectionClass = jnius.find_javaclass('java.util.Collection')
        jIteratorClass = jnius.find_javaclass('java.util.Iterator')
        jMapClass = jnius.find_javaclass('java.util.Map')
        jSetClass = jnius.find_javaclass('java.util.Set')

        jIterable = jnius.autoclass(jIterableClass.getName())
        jCollection = jnius.autoclass(jCollectionClass.getName())
        jIterator = jnius.autoclass(jIteratorClass.getName())
        jMap = jnius.autoclass(jMapClass.getName())
        jSet = jnius.autoclass(jSetClass.getName())

        class JavaCollection:
                def __init__(self, jobj):
                        self.jobj = jobj

                def __getitem__(self, key):
                        return to_java(self.jobj.get(key))

        class JavaIterable:
                def __init__(self, jobj):
                        self.jobj = jobj

                def __iter__(self):
                        return self

                def __next__(self):
                        if self.current > self.high:
                                raise StopIteration
                        else:
                                self.current += 1
                                return self.current - 1

        def to_python(data):
                if (jMapClass.isInstance(data)):
                        jmap = jnius.cast(jMap, data)
                        pdict = {'foo': 'bar'}
                        return pdict
                elif (jSetClass.isInstance(data)):
                        jset = jnius.cast(jSet, data)
                        pset = set(['foo', 'bar'])
                        return pset
                elif (jCollectionClass.isInstance(data)):
                        jcollection = jnius.cast(jCollection, data)
                        return jcollection.toArray()  # FIXME: needs recursive conversion
                elif (jIterableClass.isInstance(data)):
                        jiterable = jnius.cast(jIterable, data)
                elif (jIteratorClass.isInstance(data)):
                        jiterator = jnius.cast(jIterator, data)

                        pass  # TODO
                # TODO other Java type checks

        # ImageJ-specific utility methods

        import imglyb, jnius, numpy

        jDataset = jnius.autoclass('net.imagej.Dataset')
        jRandomAccessibleInterval = jnius.autoclass('net.imglib2.RandomAccessibleInterval')

        class ImageJPython:
                def __init__(self, ij):
                        self._ij = ij

                def ij1_to_numpy(self, imp):
                        jDataset = jnius.autoclass('net.imagej.Dataset')
                        dataset = self._ij.convert().convert(imp, jDataset)
                        return self.rai_to_numpy(dataset)

                def rai_to_numpy(self, rai):
                        result = numpy.zeros([rai.dimension(d) for d in range(rai.numDimensions() - 1, -1, -1)])
                        self._ij.op().run("copy.rai", imglyb.to_imglib(result), rai)
                        return result

                def run_macro(self, macro, args=None):
                        return self._ij.script().run("macro.ijm", macro, True, args).get()

                def to_java(self, python_value):
                        if type(python_value) == numpy.ndarray:
                                return imglyb.to_imglib(python_value)
                        return to_java(python_value)

                def from_java(self, java_value):
                        if (self._ij.convert().supports(java_value, jDataset)):
                                # HACK: Converter exists for ImagePlus -> Dataset, but not ImagePlus -> RAI.
                                java_value = self._ij.convert().convert(java_value, jDataset)
                        if (self._ij.convert().supports(java_value, jRandomAccessibleInterval)):
                                rai = self._ij.convert().convert(java_value, jRandomAccessibleInterval)
                                result = numpy.zeros([rai.dimension(d) for d in range(rai.numDimensions() - 1, -1, -1)])
                                self._ij.op().run("copy.rai", imglyb.to_imglib(result), rai)
                                return result
                        return to_python(java_value)

        ij_wrapper.util = ImageJPython(ij_wrapper)

        return ij_wrapper
