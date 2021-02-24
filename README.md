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
>>> import ndafunctor as nf
>>> s = nf.meshgrid([1,2],[3,4,5])
>>> s.eval()
array([[[1., 2.],
        [1., 2.],
        [1., 2.]],

       [[3., 3.],
        [4., 4.],
        [5., 5.]]])
>>> f = s.jit()
>>> f()
array([[[1., 2.],
        [1., 2.],
        [1., 2.]],

       [[3., 3.],
        [4., 4.],
        [5., 5.]]], dtype=float32)
>>> s.print()
Functor: #3
    transposed_raw_meshgrid
    shape=[[0, 2], [0, 3], [0, 2]]
    iexpr=[
            i0
            i2
            i1
    ]
    Functor[0]: #2
        raw_meshgrid
        shape=[[0, 1, 2], [0, 2], [0, 3]]
        iexpr=[
                0
                i0
                i1
        ]
        Functor[0]: #0
            raw_meshgrid[0]
            shape=[[0, 2], [0, 3]]
            dexpr=['ref', ['d', 'i0']]
            data=[1, 2]
        Functor[1]: #1
            raw_meshgrid[1]
            shape=[[0, 2], [0, 3]]
            dexpr=['ref', ['d', 'i1']]
            data=[3, 4, 5]
>>> print(open(f.source).read())
#include <stdio.h>
#include <math.h>

// Data
int d_meshgrid_0[] = {1,2};
int d_meshgrid_1[] = {3,4,5};

void gen_tensor3(float * tensor3)
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
            tensor3[I0_2*3*2 + I1_2*2 + I2_2] = d_meshgrid_0[i0];
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
            tensor3[I0_2*3*2 + I1_2*2 + I2_2] = d_meshgrid_1[i1];
#undef I2_2
#undef I1_2
#undef I0_2
#undef I2_1
#undef I1_1
#undef I0_1
    }
}

```