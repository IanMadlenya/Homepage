title: Scala error 'multiple overloaded alternatives of constructor RandomAccessFile define default arguments.'
date: 2014-04-26 03:30
author: Chris Stucchio
tags: scala, scala 2.11
nolinkback: true





So far, Scala 2.11 the most painless major version increment I've seen. Most of my projects compile with no problem. The following is one of the few actual errors I've run into:

    [error] /home/stucchio/src/breeze/src/main/scala/breeze/linalg/DenseMatrix.scala:51: in class DenseMatrix, multiple overloaded alternatives of constructor DenseMatrix define default arguments.
    [error] final class DenseMatrix[@specialized(Int, Float, Double) V](val rows: Int,

Apparently 2.11 is being stricter about default arguments in constructors. The fix is fairly straightforward. In 2.10, your code might look like this:

    def this(rows: Int, data: Array[V], offset: Int = 0) = ...

In 2.11, you need to do this:

    def this(rows: Int, data: Array[V], offset: Int) = ...
    def this(rows: Int, data: Array[V]) = this(rows, data, offset)

Just throwing this out there in case someone is googling.


