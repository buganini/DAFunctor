# Notice
* Still in pre-alpha development
* Runtime axis operations are not supported by design, such as:
    * Dynamic shape
    * Dynamic transpose

# Supported operations
* creation
    * array
    * zeros
    * ones
    * full
    * arange
    * meshgrid (xy)
* manipulation
    * transpose
    * stack
    * expand_dims
    * reshape
    * concatenate

# Todo
* Elementwise operations
* slicing (step=1)
* slicing (step>1)
* slice assignment (step=1)
* slice assignment (step>1)
* manipulation
    * repeat

# Example
```
> python3 tests/meshgrid_data.py

numpy [[[1 2]
  [1 2]
  [1 2]]

 [[3 3]
  [4 4]
  [5 5]]]
ndafunctor [[[1. 2.]
  [1. 2.]
  [1. 2.]]

 [[3. 3.]
  [4. 4.]
  [5. 5.]]]
===== CFG =====
{'data': OrderedDict([('d_meshgrid_0', ('float', [1, 2])),
                      ('d_meshgrid_1', ('float', [3, 4, 5]))]),
 'stmt': [['for', [2, 3]],
          ['def', ['idx', 0, 1], 0],
          ['def', ['idx', 1, 1], ['idx', 0, 0]],
          ['def', ['idx', 2, 1], ['idx', 1, 0]],
          ['def', ['idx', 0, 2], ['idx', 0, 1]],
          ['def', ['idx', 1, 2], ['idx', 2, 1]],
          ['def', ['idx', 2, 2], ['idx', 1, 1]],
          ['=',
           Functor(id=3, desc=transposed_raw_meshgrid, shape=[[0, 2], [0, 3], [0, 2]], iexpr=['i0', 'i2', 'i1'], subs=1),
           ['ref', 'd_meshgrid_0', ('idx', 0, 0)],
           2],
          ['undef', ['idx', 2, 2]],
          ['undef', ['idx', 1, 2]],
          ['undef', ['idx', 0, 2]],
          ['undef', ['idx', 2, 1]],
          ['undef', ['idx', 1, 1]],
          ['undef', ['idx', 0, 1]],
          ['endfor'],
          ['for', [2, 3]],
          ['def', ['idx', 0, 1], ['+', [0, 1]]],
          ['def', ['idx', 1, 1], ['idx', 0, 0]],
          ['def', ['idx', 2, 1], ['idx', 1, 0]],
          ['def', ['idx', 0, 2], ['idx', 0, 1]],
          ['def', ['idx', 1, 2], ['idx', 2, 1]],
          ['def', ['idx', 2, 2], ['idx', 1, 1]],
          ['=',
           Functor(id=3, desc=transposed_raw_meshgrid, shape=[[0, 2], [0, 3], [0, 2]], iexpr=['i0', 'i2', 'i1'], subs=1),
           ['ref', 'd_meshgrid_1', ('idx', 1, 0)],
           2],
          ['undef', ['idx', 2, 2]],
          ['undef', ['idx', 1, 2]],
          ['undef', ['idx', 0, 2]],
          ['undef', ['idx', 2, 1]],
          ['undef', ['idx', 1, 1]],
          ['undef', ['idx', 0, 1]],
          ['endfor']]}
===== C =====
ndafunctor-C [[[1. 2.]
  [1. 2.]
  [1. 2.]]

 [[3. 3.]
  [4. 4.]
  [5. 5.]]]

> cat __jit__/gen_output.c
#include <stdio.h>
#include <math.h>

// Data
float d_meshgrid_0[] = {1,2};
float d_meshgrid_1[] = {3,4,5};

void gen_output(float * output)
{
    for(int i0=0;i0<2;i0++)
      for(int i1=0;i1<3;i1++)
    {
#define I0_1 (0)
#define I1_1 (i0)
#define I2_1 (i1)
#define I0_2 (I0_1)
#define I1_2 (I2_1)
#define I2_2 (I1_1)
            output[I0_2*3*2 + I1_2*2 + I2_2] = d_meshgrid_0[i0];
#undef I2_2
#undef I1_2
#undef I0_2
#undef I2_1
#undef I1_1
#undef I0_1
    }
    for(int i0=0;i0<2;i0++)
      for(int i1=0;i1<3;i1++)
    {
#define I0_1 ((0+1))
#define I1_1 (i0)
#define I2_1 (i1)
#define I0_2 (I0_1)
#define I1_2 (I2_1)
#define I2_2 (I1_1)
            output[I0_2*3*2 + I1_2*2 + I2_2] = d_meshgrid_1[i1];
#undef I2_2
#undef I1_2
#undef I0_2
#undef I2_1
#undef I1_1
#undef I0_1
    }
}

```