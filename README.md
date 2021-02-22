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

# Todo
* Elementwise operations
* slicing (step=1)
* slicing (step>1)
* slice assignment (step=1)
* slice assignment (step>1)
* manipulation
    * repeat
    * concatenate

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
          ['endfor']],
 'symbols': OrderedDict([('output', ('float', [[0, 2], [0, 3], [0, 2]]))])}
===== C =====
Generated tests/../test-build/meshgrid_data.py.c
#include <stdio.h>

// Tensors
float output[12];

// Data
float d_meshgrid_0[] = {1,2};
float d_meshgrid_1[] = {3,4,5};

int main(int argc, char *argv[]){
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

    // Check outputs
    printf("output\n");
    for(int i=0;i<12;i++){
        if(i % 12 == 0) printf("[");
        if(i % 6 == 0) printf("[");
        if(i % 2 == 0) printf("[");
        printf("%.2f", output[i]);
        int print_space=1;
        if((i+1) % 12 == 0){ printf("]"); print_space=0; }
        if((i+1) % 6 == 0){ printf("]"); print_space=0; }
        if((i+1) % 2 == 0){ printf("]"); print_space=0; }
        if(print_space) printf(" ");
    }
    printf("\n");
    return 0;
}

output
[[[1.00 2.00][1.00 2.00][1.00 2.00]][[3.00 3.00][4.00 4.00][5.00 5.00]]]
```