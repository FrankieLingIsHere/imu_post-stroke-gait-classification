#pragma once
#include "compat.h"
#include <alloca.h>
#include <cstring>
// Upstream mkdir helper uses this GNU libc macro, absent in Android bionic.
#ifndef strdupa
#define strdupa(value) __extension__ ({ const char* source_=(value); size_t size_=std::strlen(source_)+1; char* copy_=static_cast<char*>(alloca(size_)); std::memcpy(copy_,source_,size_); copy_; })
#endif
