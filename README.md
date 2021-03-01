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
    * repeat (axis != None)

# Todo
* Elementwise operations
* slicing (step=1)
* slicing (step>1)
* slice assignment (step=1)
* slice assignment (step>1)

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
    shape=(2, 3, 2)
    iexpr=[
            i0
            i2
            i1
    ]
    Functor[0]: #2
        raw_meshgrid
        shape=(2, 2, 3)
        ranges=[[(0, 1, 1), (0, 2, 1), (0, 3, 1)], [(1, 1, 1), (0, 2, 1), (0, 3, 1)]]
        iexpr=[
                0
                i0
                i1
        ]
        Functor[0]: #0
            raw_meshgrid[0]
            shape=(2, 3)
            dexpr=['ref', ['d', 'i0']]
            data=[1, 2]
        Functor[1]: #1
            raw_meshgrid[1]
            shape=(2, 3)
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
        int i0_0_1 = (0+0);
        int i1_0_1 = (i0+0);
        int i2_0_1 = (i1+0);
        int i0_0_2 = (i0_0_1+0);
        int i1_0_2 = (i2_0_1+0);
        int i2_0_2 = (i1_0_1+0);
        tensor3[i0_0_2*3*2 + i1_0_2*2 + i2_0_2] = d_meshgrid_0[i0];
    }
    for(int i0=0;i0<2;i0++)
      for(int i1=0;i1<3;i1++)
    {
        int i0_0_1 = (0+1);
        int i1_0_1 = (i0+0);
        int i2_0_1 = (i1+0);
        int i0_0_2 = (i0_0_1+0);
        int i1_0_2 = (i2_0_1+0);
        int i2_0_2 = (i1_0_1+0);
        tensor3[i0_0_2*3*2 + i1_0_2*2 + i2_0_2] = d_meshgrid_1[i1];
    }
}

```