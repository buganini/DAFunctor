# NOTICE
* Variable-dimension tensor is not supported
* Compile/Run-time is kind of vague

# Example
```
> python3 tests/0.py

numpy [[[1 2]
  [1 2]
  [1 2]]

 [[3 3]
  [4 4]
  [5 5]]]
intro-tensor [[[1 2]
  [1 2]
  [1 2]]

 [[3 3]
  [4 4]
  [5 5]]]
===== CFG =====
{'cfg': [('for', [2, 3, 2]),
         ('=',
          Tensor: transpose=[0, 2, 1], offset=None,
          ('ref',
           ('ref',
            ('term', 'reg140273157350144'),
            ('ref', 'idx', ('ref', 'trans0_2_1', ('term', '0')))),
           ('ref',
            'idx',
            ('ref',
             'trans0_2_1',
             ('+',
              ('ref', 'idx', ('ref', 'trans0_2_1', ('term', '0'))),
              ('term', '1')))))),
         ('endfor',)],
 'data': OrderedDict([('trans0_2_1', ('int', [0, 2, 1])),
                      ('reg140273157475648', ('float', [1, 2])),
                      ('reg140273152077120', ('float', [3, 4, 5])),
                      ('reg140273157350144',
                       ('float *',
                        ['reg140273157475648', 'reg140273152077120']))]),
 'symbols': OrderedDict([('output', ('float', [2, 3, 2]))])}
```

# Test generated C code
```
#include <stdio.h>

// Tensors
float output[12];

// Data
int trans0_2_1[] = {0,2,1};
float reg140030912884480[] = {1,2};
float reg140030907485632[] = {3,4,5};
float * reg140030912758976[] = {reg140030912884480,reg140030907485632};


int main(int argc, char *argv[]){
    int idx[3];
    for(idx[0]=0;idx[0]<2;idx[0]++)
    for(idx[1]=0;idx[1]<3;idx[1]++)
        for(idx[2]=0;idx[2]<2;idx[2]++)
    {
        output[idx[0]*3*2 + idx[1]*2 + idx[2]] = reg140030912758976[idx[trans0_2_1[0]]][idx[trans0_2_1[(idx[trans0_2_1[0]]+1)]]];
    }


    // Check output
    for(int i=0;i<12;i+=1){
        printf("%f ", output[i]);
    }
}


Output:
1.000000 2.000000 1.000000 2.000000 1.000000 2.000000 3.000000 3.000000 4.000000 4.000000 5.000000 5.000000
```