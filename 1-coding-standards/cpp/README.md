

### Language Style and Standards

Do not use C++ with classes. Use modern C++ instead. 


#### When accesing elements in containers, use at() instead of []

```cpp
  std::vector<double> v = {1,2,3};
  double v1 = v[0];  // Avoid
  double v2 = v.at(0); // Ok. Bounds checked
```

#### To avoid multiple includes use pragma once (when supported)

Example, instead of 

```cpp
#ifndef MYHEADER_H
#define MYHEADER_H
// ... the contents of this header file
#endif
```

Use

```cpp
#pragma once
```
