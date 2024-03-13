typedef unsigned char   undefined;

typedef unsigned char    byte;
typedef unsigned char    dwfenc;
typedef unsigned int    dword;
typedef unsigned long    qword;
typedef long    sqword;
typedef unsigned char    uchar;
typedef unsigned int    uint;
typedef unsigned long    ulong;
typedef unsigned char    undefined1;
typedef unsigned int    undefined4;
typedef unsigned long    undefined8;
typedef unsigned short    word;
typedef struct eh_frame_hdr eh_frame_hdr, *Peh_frame_hdr;

struct eh_frame_hdr {
    byte eh_frame_hdr_version; // Exception Handler Frame Header Version
    dwfenc eh_frame_pointer_encoding; // Exception Handler Frame Pointer Encoding
    dwfenc eh_frame_desc_entry_count_encoding; // Encoding of # of Exception Handler FDEs
    dwfenc eh_frame_table_encoding; // Exception Handler Table Encoding
};

typedef struct fde_table_entry fde_table_entry, *Pfde_table_entry;

struct fde_table_entry {
    dword initial_loc; // Initial Location
    dword data_loc; // Data location
};

typedef ulong size_t;

typedef ulong __ARRAY_SIZE_TYPE__;

typedef qword __uint64_t;

typedef dword __uint32_t;

typedef uint u_int;

typedef sqword __int64_t;

typedef struct Elf64_Rela Elf64_Rela, *PElf64_Rela;

typedef struct Elf64_Rela Elf_Rela;

typedef __uint64_t uint64_t;

typedef uint64_t Elf64_Addr;

typedef uint64_t Elf64_Xword;

typedef __int64_t int64_t;

typedef int64_t Elf64_Sxword;

struct Elf64_Rela {
    Elf64_Addr r_offset;
    Elf64_Xword r_info;
    Elf64_Sxword r_addend;
};

typedef Elf64_Addr Elf_Addr;

typedef __uint64_t __uintptr_t;

typedef __uint64_t __size_t;

typedef __uint32_t uint32_t;

typedef __uintptr_t uintptr_t;


// WARNING! conflicting data type names: /DWARF/stdlib.h/size_t - /stddef.h/size_t

typedef long __time_t;

typedef struct evp_pkey_ctx_st evp_pkey_ctx_st, *Pevp_pkey_ctx_st;

struct evp_pkey_ctx_st {
};

typedef struct evp_pkey_ctx_st EVP_PKEY_CTX;

typedef __time_t time_t;

typedef struct allocator<int> allocator<int>, *Pallocator<int>;

struct allocator<int> { // PlaceHolder Structure
};

typedef dword initializer_list;

typedef struct __new_allocator<int> __new_allocator<int>, *P__new_allocator<int>;

struct __new_allocator<int> { // PlaceHolder Structure
};

typedef struct vector<unsigned_char,std::allocator<unsigned_char>> vector<unsigned_char,std::allocator<unsigned_char>>, *Pvector<unsigned_char,std::allocator<unsigned_char>>;

struct vector<unsigned_char,std::allocator<unsigned_char>> { // PlaceHolder Structure
};

typedef struct allocator<unsigned_char> allocator<unsigned_char>, *Pallocator<unsigned_char>;

struct allocator<unsigned_char> { // PlaceHolder Structure
};

typedef struct __new_allocator __new_allocator, *P__new_allocator;

struct __new_allocator { // PlaceHolder Structure
};

typedef struct _Vector_base<unsigned_char,std::allocator<unsigned_char>> _Vector_base<unsigned_char,std::allocator<unsigned_char>>, *P_Vector_base<unsigned_char,std::allocator<unsigned_char>>;

struct _Vector_base<unsigned_char,std::allocator<unsigned_char>> { // PlaceHolder Structure
};

typedef struct vector<int,std::allocator<int>> vector<int,std::allocator<int>>, *Pvector<int,std::allocator<int>>;

struct vector<int,std::allocator<int>> { // PlaceHolder Structure
};

typedef struct __new_allocator<unsigned_char> __new_allocator<unsigned_char>, *P__new_allocator<unsigned_char>;

struct __new_allocator<unsigned_char> { // PlaceHolder Structure
};

typedef dword random_access_iterator_tag;

typedef struct allocator<char> allocator<char>, *Pallocator<char>;

struct allocator<char> { // PlaceHolder Structure
};

typedef struct allocator allocator, *Pallocator;

struct allocator { // PlaceHolder Structure
};

typedef struct basic_ostream basic_ostream, *Pbasic_ostream;

struct basic_ostream { // PlaceHolder Structure
};

typedef struct _Vector_base<int,std::allocator<int>> _Vector_base<int,std::allocator<int>>, *P_Vector_base<int,std::allocator<int>>;

struct _Vector_base<int,std::allocator<int>> { // PlaceHolder Structure
};

typedef dword forward_iterator_tag;

typedef struct basic_ostream<char,std::char_traits<char>> basic_ostream<char,std::char_traits<char>>, *Pbasic_ostream<char,std::char_traits<char>>;

struct basic_ostream<char,std::char_traits<char>> { // PlaceHolder Structure
};

typedef dword iterator_category;

typedef dword difference_type;

typedef dword basic_string;

typedef struct basic_string<char,std::char_traits<char>,std::allocator<char>> basic_string<char,std::char_traits<char>,std::allocator<char>>, *Pbasic_string<char,std::char_traits<char>,std::allocator<char>>;

struct basic_string<char,std::char_traits<char>,std::allocator<char>> { // PlaceHolder Structure
};

typedef struct _Alloc_hider _Alloc_hider, *P_Alloc_hider;

struct _Alloc_hider { // PlaceHolder Structure
};

typedef struct _Guard _Guard, *P_Guard;

struct _Guard { // PlaceHolder Structure
};

typedef struct Init Init, *PInit;

struct Init { // PlaceHolder Structure
};

typedef struct _Vector_impl _Vector_impl, *P_Vector_impl;

struct _Vector_impl { // PlaceHolder Structure
};

typedef struct _Vector_impl_data _Vector_impl_data, *P_Vector_impl_data;

struct _Vector_impl_data { // PlaceHolder Structure
};

typedef struct Elf64_Shdr Elf64_Shdr, *PElf64_Shdr;

typedef enum Elf_SectionHeaderType {
    SHT_NULL=0,
    SHT_PROGBITS=1,
    SHT_SYMTAB=2,
    SHT_STRTAB=3,
    SHT_RELA=4,
    SHT_HASH=5,
    SHT_DYNAMIC=6,
    SHT_NOTE=7,
    SHT_NOBITS=8,
    SHT_REL=9,
    SHT_SHLIB=10,
    SHT_DYNSYM=11,
    SHT_INIT_ARRAY=14,
    SHT_FINI_ARRAY=15,
    SHT_PREINIT_ARRAY=16,
    SHT_GROUP=17,
    SHT_SYMTAB_SHNDX=18,
    SHT_ANDROID_REL=1610612737,
    SHT_ANDROID_RELA=1610612738,
    SHT_GNU_ATTRIBUTES=1879048181,
    SHT_GNU_HASH=1879048182,
    SHT_GNU_LIBLIST=1879048183,
    SHT_CHECKSUM=1879048184,
    SHT_SUNW_move=1879048186,
    SHT_SUNW_COMDAT=1879048187,
    SHT_SUNW_syminfo=1879048188,
    SHT_GNU_verdef=1879048189,
    SHT_GNU_verneed=1879048190,
    SHT_GNU_versym=1879048191
} Elf_SectionHeaderType;

struct Elf64_Shdr {
    dword sh_name;
    enum Elf_SectionHeaderType sh_type;
    qword sh_flags;
    qword sh_addr;
    qword sh_offset;
    qword sh_size;
    dword sh_link;
    dword sh_info;
    qword sh_addralign;
    qword sh_entsize;
};


// WARNING! conflicting data type names: /ELF/Elf64_Rela - /DWARF/elf64.h/Elf64_Rela

typedef enum Elf64_DynTag {
    DT_NULL=0,
    DT_NEEDED=1,
    DT_PLTRELSZ=2,
    DT_PLTGOT=3,
    DT_HASH=4,
    DT_STRTAB=5,
    DT_SYMTAB=6,
    DT_RELA=7,
    DT_RELASZ=8,
    DT_RELAENT=9,
    DT_STRSZ=10,
    DT_SYMENT=11,
    DT_INIT=12,
    DT_FINI=13,
    DT_SONAME=14,
    DT_RPATH=15,
    DT_SYMBOLIC=16,
    DT_REL=17,
    DT_RELSZ=18,
    DT_RELENT=19,
    DT_PLTREL=20,
    DT_DEBUG=21,
    DT_TEXTREL=22,
    DT_JMPREL=23,
    DT_BIND_NOW=24,
    DT_INIT_ARRAY=25,
    DT_FINI_ARRAY=26,
    DT_INIT_ARRAYSZ=27,
    DT_FINI_ARRAYSZ=28,
    DT_RUNPATH=29,
    DT_FLAGS=30,
    DT_PREINIT_ARRAY=32,
    DT_PREINIT_ARRAYSZ=33,
    DT_RELRSZ=35,
    DT_RELR=36,
    DT_RELRENT=37,
    DT_ANDROID_REL=1610612751,
    DT_ANDROID_RELSZ=1610612752,
    DT_ANDROID_RELA=1610612753,
    DT_ANDROID_RELASZ=1610612754,
    DT_ANDROID_RELR=1879040000,
    DT_ANDROID_RELRSZ=1879040001,
    DT_ANDROID_RELRENT=1879040003,
    DT_GNU_PRELINKED=1879047669,
    DT_GNU_CONFLICTSZ=1879047670,
    DT_GNU_LIBLISTSZ=1879047671,
    DT_CHECKSUM=1879047672,
    DT_PLTPADSZ=1879047673,
    DT_MOVEENT=1879047674,
    DT_MOVESZ=1879047675,
    DT_FEATURE_1=1879047676,
    DT_POSFLAG_1=1879047677,
    DT_SYMINSZ=1879047678,
    DT_SYMINENT=1879047679,
    DT_GNU_XHASH=1879047924,
    DT_GNU_HASH=1879047925,
    DT_TLSDESC_PLT=1879047926,
    DT_TLSDESC_GOT=1879047927,
    DT_GNU_CONFLICT=1879047928,
    DT_GNU_LIBLIST=1879047929,
    DT_CONFIG=1879047930,
    DT_DEPAUDIT=1879047931,
    DT_AUDIT=1879047932,
    DT_PLTPAD=1879047933,
    DT_MOVETAB=1879047934,
    DT_SYMINFO=1879047935,
    DT_VERSYM=1879048176,
    DT_RELACOUNT=1879048185,
    DT_RELCOUNT=1879048186,
    DT_FLAGS_1=1879048187,
    DT_VERDEF=1879048188,
    DT_VERDEFNUM=1879048189,
    DT_VERNEED=1879048190,
    DT_VERNEEDNUM=1879048191,
    DT_AUXILIARY=2147483645,
    DT_FILTER=2147483647
} Elf64_DynTag;

typedef enum Elf_ProgramHeaderType {
    PT_NULL=0,
    PT_LOAD=1,
    PT_DYNAMIC=2,
    PT_INTERP=3,
    PT_NOTE=4,
    PT_SHLIB=5,
    PT_PHDR=6,
    PT_TLS=7,
    PT_GNU_EH_FRAME=1685382480,
    PT_GNU_STACK=1685382481,
    PT_GNU_RELRO=1685382482
} Elf_ProgramHeaderType;

typedef struct Elf64_Dyn Elf64_Dyn, *PElf64_Dyn;

struct Elf64_Dyn {
    enum Elf64_DynTag d_tag;
    qword d_val;
};

typedef struct Elf64_Phdr Elf64_Phdr, *PElf64_Phdr;

struct Elf64_Phdr {
    enum Elf_ProgramHeaderType p_type;
    dword p_flags;
    qword p_offset;
    qword p_vaddr;
    qword p_paddr;
    qword p_filesz;
    qword p_memsz;
    qword p_align;
};

typedef struct Elf64_Sym Elf64_Sym, *PElf64_Sym;

struct Elf64_Sym {
    dword st_name;
    byte st_info;
    byte st_other;
    word st_shndx;
    qword st_value;
    qword st_size;
};

typedef struct Elf64_Ehdr Elf64_Ehdr, *PElf64_Ehdr;

struct Elf64_Ehdr {
    byte e_ident_magic_num;
    char e_ident_magic_str[3];
    byte e_ident_class;
    byte e_ident_data;
    byte e_ident_version;
    byte e_ident_osabi;
    byte e_ident_abiversion;
    byte e_ident_pad[7];
    word e_type;
    word e_machine;
    dword e_version;
    qword e_entry;
    qword e_phoff;
    qword e_shoff;
    dword e_flags;
    word e_ehsize;
    word e_phentsize;
    word e_phnum;
    word e_shentsize;
    word e_shnum;
    word e_shstrndx;
};

typedef struct ElfNote_8_4 ElfNote_8_4, *PElfNote_8_4;

struct ElfNote_8_4 {
    dword namesz; // Length of name field
    dword descsz; // Length of description field
    dword type; // Vendor specific type
    char name[8]; // Vendor name
    byte description[4]; // Blob value
};




int _init(EVP_PKEY_CTX *ctx)

{
  int iVar1;
  
  frame_dummy();
  iVar1 = __do_global_ctors_aux();
  return iVar1;
}



void FUN_00401390(void)

{
                    // WARNING: Treating indirect jump as call
  (*(code *)(undefined *)0x0)();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

time_t time(time_t *__timer)

{
  time_t tVar1;
  
  tVar1 = time(__timer);
  return tVar1;
}



void __thiscall std::allocator<char>::~allocator(allocator<char> *this)

{
  ~allocator(this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

size_t strlen(char *__s)

{
  size_t sVar1;
  
  sVar1 = strlen(__s);
  return sVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__throw_bad_alloc(void)

{
  __throw_bad_alloc();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string
               (basic_string *param_1)

{
  basic_string(param_1);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::basic_ostream<char, std::char_traits<char> >& std::endl<char, std::char_traits<char>
// >(std::basic_ostream<char, std::char_traits<char> >&)

basic_ostream * std::endl<char,std::char_traits<char>>(basic_ostream *param_1)

{
  do {
                    // WARNING: Do nothing block with infinite loop
  } while( true );
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__throw_length_error(char *param_1)

{
  __throw_length_error(param_1);
  return;
}



void __thiscall
std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string
          (basic_string<char,std::char_traits<char>,std::allocator<char>> *this)

{
  ~basic_string(this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

int atexit(__func *__func)

{
  int iVar1;
  
  iVar1 = atexit(__func);
  return iVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_set_length
               (ulong param_1)

{
  _M_set_length(param_1);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::size(void)

{
  size();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__throw_logic_error(char *param_1)

{
  __throw_logic_error(param_1);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void srand(uint __seed)

{
  srand(__seed);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__throw_bad_array_new_length(void)

{
  __throw_bad_array_new_length();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_local_data
               (void)

{
  _M_local_data();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_data
               (char *param_1)

{
  _M_data(param_1);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void * memmove(void *__dest,void *__src,size_t __n)

{
  void *pvVar1;
  
  pvVar1 = memmove(__dest,__src,__n);
  return pvVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

basic_ostream * std::operator<<(basic_ostream *param_1,char *param_2)

{
  basic_ostream *pbVar1;
  
  pbVar1 = operator<<(param_1,param_2);
  return pbVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void * operator_new(ulong param_1)

{
  void *pvVar1;
  
  pvVar1 = operator_new(param_1);
  return pvVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void operator_delete(void *param_1,ulong param_2)

{
  operator_delete(param_1,param_2);
  return;
}



void __thiscall
std::basic_ostream<char,std::char_traits<char>>::operator<<
          (basic_ostream<char,std::char_traits<char>> *this,
          _func_basic_ostream_ptr_basic_ostream_ptr *param_1)

{
  operator<<(this,param_1);
  return;
}



void __thiscall
std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_Alloc_hider::
_Alloc_hider(_Alloc_hider *this,char *param_1,allocator *param_2)

{
  _Alloc_hider(this,param_1,param_2);
  return;
}



void _init_tls(void)

{
  _init_tls();
  return;
}



void __thiscall std::allocator<char>::~allocator(allocator<char> *this)

{
  ~allocator(this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_data(void)

{
  _M_data();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_S_copy_chars
               (char *param_1,char *param_2,char *param_3)

{
  _S_copy_chars(param_1,param_2,param_3);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void * memcpy(void *__dest,void *__src,size_t __n)

{
  void *pvVar1;
  
  pvVar1 = memcpy(__dest,__src,__n);
  return pvVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_dispose(void)

{
  _M_dispose();
  return;
}



void __thiscall std::ios_base::Init::Init(Init *this)

{
  Init(this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

int rand(void)

{
  int iVar1;
  
  iVar1 = rand();
  return iVar1;
}



void __gxx_personality_v0(void)

{
  do {
                    // WARNING: Do nothing block with infinite loop
  } while( true );
}



void _Unwind_Resume(void)

{
                    // WARNING: Subroutine does not return
  _Unwind_Resume();
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::allocator<char>::allocator(void)

{
  allocator();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_create
               (ulong *param_1,ulong param_2)

{
  _M_create(param_1,param_2);
  return;
}



void __cxa_atexit(void)

{
  __cxa_atexit();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void exit(int __status)

{
                    // WARNING: Subroutine does not return
  exit(__status);
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_capacity
               (ulong param_1)

{
  _M_capacity(param_1);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::operator[]
               (ulong param_1)

{
  operator[](param_1);
  return;
}



// std::ios_base::Init::~Init()

void __thiscall std::ios_base::Init::~Init(Init *this)

{
  do {
                    // WARNING: Do nothing block with infinite loop
  } while( true );
}



// WARNING: Removing unreachable block (ram,0x004016d2)
// WARNING: Removing unreachable block (ram,0x004016ba)
// WARNING: Removing unreachable block (ram,0x004016b2)
// WARNING: Removing unreachable block (ram,0x0040168c)
// WARNING: Removing unreachable block (ram,0x004016d4)
// WARNING: Removing unreachable block (ram,0x004016db)
// WARNING: Removing unreachable block (ram,0x004016a0)
// WARNING: Removing unreachable block (ram,0x004016a4)
// WARNING: Removing unreachable block (ram,0x004016ad)
// WARNING: Removing unreachable block (ram,0x004016cb)
// WARNING: Removing unreachable block (ram,0x004016eb)
// WARNING: Unknown calling convention

void _start(char **ap,_func_void *cleanup)

{
  char cVar1;
  char *pcVar2;
  uint32_t cpu_stdext_feature;
  int __status;
  char *pcVar3;
  Elf_Addr target;
  uint32_t cpu_stdext_feature2;
  char **env_00;
  char **env;
  uint32_t cpu_feature2;
  uint32_t cpu_feature;
  Elf_Addr *where;
  Elf_Rela *r;
  char **argv_00;
  char **argv;
  int argc;
  char *pcVar4;
  
  pcVar2 = *ap;
  argc = (int)pcVar2;
  env_00 = ap + (long)argc + 2;
  if (environ == (char **)0x0) {
    environ = env_00;
  }
  argv_00 = ap + 1;
  if ((0 < argc) && (pcVar4 = *argv_00, pcVar3 = pcVar4, pcVar4 != (char *)0x0)) {
    do {
      do {
        __progname = pcVar3;
        pcVar3 = pcVar4 + 1;
        cVar1 = *pcVar4;
        pcVar4 = pcVar3;
      } while (cVar1 == '/');
      pcVar3 = __progname;
    } while (cVar1 != '\0');
  }
  atexit((__func *)cleanup);
  handle_static_init(argc,argv_00,env_00);
  __status = main((ulong)pcVar2 & 0xffffffff,argv_00,env_00);
                    // WARNING: Subroutine does not return
  exit(__status);
}



// WARNING: Removing unreachable block (ram,0x0040173c)
// WARNING: Removing unreachable block (ram,0x00401766)
// WARNING: Removing unreachable block (ram,0x0040176a)
// WARNING: Removing unreachable block (ram,0x00401770)
// WARNING: Removing unreachable block (ram,0x00401773)
// WARNING: Removing unreachable block (ram,0x00401777)
// WARNING: Removing unreachable block (ram,0x00401785)
// WARNING: Removing unreachable block (ram,0x00401789)
// WARNING: Removing unreachable block (ram,0x00401799)
// WARNING: Removing unreachable block (ram,0x004017a7)
// WARNING: Removing unreachable block (ram,0x00401790)
// WARNING: Removing unreachable block (ram,0x004017b4)
// WARNING: Removing unreachable block (ram,0x004017d0)
// WARNING: Removing unreachable block (ram,0x004017d4)
// WARNING: Removing unreachable block (ram,0x004017da)
// WARNING: Removing unreachable block (ram,0x004017dd)
// WARNING: Removing unreachable block (ram,0x004017e1)
// WARNING: Removing unreachable block (ram,0x004017ef)
// WARNING: Removing unreachable block (ram,0x004017f3)
// WARNING: Removing unreachable block (ram,0x00401809)
// WARNING: Removing unreachable block (ram,0x00401817)
// WARNING: Removing unreachable block (ram,0x00401800)
// WARNING: Unknown calling convention

void handle_static_init(int argc,char **argv,char **env)

{
  _func_void_int_char_ptr_ptr_char_ptr_ptr *fn;
  
  return;
}



// WARNING: Removing unreachable block (ram,0x0040185d)
// WARNING: Removing unreachable block (ram,0x00401872)
// WARNING: Removing unreachable block (ram,0x00401885)
// WARNING: Removing unreachable block (ram,0x00401897)
// WARNING: Removing unreachable block (ram,0x00401880)
// WARNING: Unknown calling convention

void finalizer(void)

{
  _func_void *fn;
  size_t n;
  
  _fini();
  return;
}



// WARNING: Removing unreachable block (ram,0x004018b3)
// WARNING: Removing unreachable block (ram,0x004018bf)

void deregister_tm_clones(void)

{
  return;
}



// WARNING: Removing unreachable block (ram,0x004018f4)
// WARNING: Removing unreachable block (ram,0x00401900)

void register_tm_clones(void)

{
  return;
}



// WARNING: Removing unreachable block (ram,0x00401948)
// WARNING: Removing unreachable block (ram,0x00401950)

void __do_global_dtors_aux(void)

{
  if (completed_1 != '\0') {
    return;
  }
  deregister_tm_clones();
  completed_1 = 1;
  return;
}



// WARNING: Removing unreachable block (ram,0x004018f4)
// WARNING: Removing unreachable block (ram,0x00401900)

void frame_dummy(void)

{
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// __gthread_trigger()

void __gthread_trigger(void)

{
  __gthread_active = 1;
  return;
}



// verify(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >)

void verify(basic_string param_1)

{
  byte bVar1;
  byte bVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  ulong uVar6;
  int *piVar7;
  undefined4 *puVar8;
  byte *pbVar9;
  time_t tVar10;
  char *pcVar11;
  basic_ostream *pbVar12;
  ulong uVar13;
  undefined4 in_register_0000003c;
  basic_string<char,std::char_traits<char>,std::allocator<char>> local_d8 [32];
  vector<unsigned_char,std::allocator<unsigned_char>> local_b8 [32];
  allocator local_98;
  undefined local_97;
  undefined local_96;
  undefined local_95;
  undefined local_94;
  undefined local_93;
  undefined local_92;
  undefined local_91;
  undefined local_90;
  undefined local_8f;
  undefined local_8e;
  undefined local_8d;
  undefined local_8c;
  undefined local_8b;
  undefined local_8a;
  undefined local_89;
  undefined local_88;
  undefined local_87;
  undefined local_86;
  undefined local_85;
  undefined local_84;
  undefined local_83;
  undefined local_82;
  undefined local_81;
  undefined local_80;
  undefined local_7f;
  undefined local_7e;
  undefined local_7d;
  undefined local_7c;
  undefined local_7b;
  undefined local_7a;
  undefined local_79;
  undefined local_78;
  undefined local_77;
  undefined local_76;
  undefined local_75;
  undefined local_74;
  undefined local_73;
  undefined local_72;
  undefined local_71;
  undefined local_70;
  undefined local_6f;
  undefined local_6e;
  undefined local_6d;
  undefined local_6c;
  undefined local_6b;
  undefined local_6a;
  undefined local_69;
  undefined local_68;
  undefined local_67;
  undefined local_66;
  undefined local_65;
  undefined local_64;
  undefined local_63;
  undefined local_62;
  undefined local_61;
  undefined local_60;
  undefined local_5f;
  undefined local_5e;
  undefined local_5d;
  undefined local_5c;
  undefined local_5b;
  undefined local_5a;
  undefined local_59;
  undefined local_58;
  undefined local_57;
  undefined local_56;
  undefined local_55;
  undefined local_54;
  undefined local_53;
  undefined local_52;
  undefined local_51;
  undefined local_50;
  undefined local_4f;
  allocator<unsigned_char> local_42;
  allocator local_41;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  
  local_98 = (allocator)0x3f;
  local_97 = 0x42;
  local_96 = 0x38;
  local_95 = 0x5f;
  local_94 = 0x7a;
  local_93 = 0x57;
  local_92 = 0x71;
  local_91 = 0x74;
  local_90 = 0x66;
  local_8f = 0x44;
  local_8e = 0x47;
  local_8d = 0x32;
  local_8c = 0x3d;
  local_8b = 0x16;
  local_8a = 99;
  local_89 = 0x1f;
  local_88 = 0x12;
  local_87 = 0x1a;
  local_86 = 0x12;
  local_85 = 0x5c;
  local_84 = 0x2a;
  local_83 = 3;
  local_82 = 100;
  local_81 = 0x1c;
  local_80 = 0x15;
  local_7f = 0x40;
  local_7e = 1;
  local_7d = 0x3f;
  local_7c = 0x4c;
  local_7b = 2;
  local_7a = 0x3a;
  local_79 = 0x30;
  local_78 = 0x1d;
  local_77 = 0x7c;
  local_76 = 0x69;
  local_75 = 0x4d;
  local_74 = 0x19;
  local_73 = 0x5f;
  local_72 = 0x48;
  local_71 = 0x5e;
  local_70 = 0x20;
  local_6f = 3;
  local_6e = 0x17;
  local_6d = 9;
  local_6c = 0x52;
  local_6b = 0x6b;
  local_6a = 0x4c;
  local_69 = 0x65;
  local_68 = 0x6f;
  local_67 = 0x48;
  local_66 = 6;
  local_65 = 0x5b;
  local_64 = 0x2b;
  local_63 = 0x28;
  local_62 = 0x40;
  local_61 = 0x2e;
  local_60 = 0x4e;
  local_5f = 0xb;
  local_5e = 0x16;
  local_5d = 0x31;
  local_5c = 0x30;
  local_5b = 0x56;
  local_5a = 0x21;
  local_59 = 0x6e;
  local_58 = 0x2d;
  local_57 = 0x30;
  local_56 = 0x4b;
  local_55 = 0x1c;
  local_54 = 0x10;
  local_53 = 4;
  local_52 = 0x3f;
  local_51 = 0x18;
  local_50 = 0x41;
  local_4f = 0x34;
  std::allocator<unsigned_char>::allocator();
                    // try { // try from 00401b54 to 00401b58 has its CatchHandler @ 00401f04
  std::vector<unsigned_char,std::allocator<unsigned_char>>::vector
            ((initializer_list)local_b8,&local_98);
  std::allocator<unsigned_char>::~allocator(&local_42);
  local_2c = 0;
  while( true ) {
    uVar13 = (ulong)local_2c;
    uVar6 = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::size();
    if (uVar6 <= uVar13) break;
    pbVar9 = (byte *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                               (local_b8,(long)local_2c);
    bVar2 = *pbVar9;
                    // try { // try from 00401b9e to 00401c8b has its CatchHandler @ 00401f43
    pbVar9 = (byte *)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
                     operator[](CONCAT44(in_register_0000003c,param_1));
    bVar1 = *pbVar9;
    pbVar9 = (byte *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                               (local_b8,(long)local_2c);
    *pbVar9 = bVar1 ^ bVar2;
    local_2c = local_2c + 1;
  }
  local_30 = 0;
  while( true ) {
    uVar13 = (ulong)local_30;
    uVar6 = std::vector<unsigned_char,std::allocator<unsigned_char>>::size();
    if (uVar6 <= uVar13) break;
    pbVar9 = (byte *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                               (local_b8,(long)local_30);
    bVar2 = *pbVar9;
    iVar5 = local_30 * 10;
    uVar6 = std::vector<int,std::allocator<int>>::size();
    piVar7 = (int *)std::vector<int,std::allocator<int>>::operator[]
                              ((vector<int,std::allocator<int>> *)data,
                               (ulong)(long)(iVar5 + 0xc) % uVar6);
    iVar5 = *piVar7;
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::size();
    pcVar11 = (char *)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
                      operator[](CONCAT44(in_register_0000003c,param_1));
    cVar3 = *pcVar11;
    uVar6 = std::vector<int,std::allocator<int>>::size();
    puVar8 = (undefined4 *)
             std::vector<int,std::allocator<int>>::operator[]
                       ((vector<int,std::allocator<int>> *)data,(ulong)(long)(cVar3 + iVar5) % uVar6
                       );
    uVar4 = *puVar8;
    pbVar9 = (byte *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                               (local_b8,(long)local_30);
    *pbVar9 = (byte)uVar4 ^ bVar2;
    local_30 = local_30 + 1;
  }
  local_34 = 5;
  while( true ) {
    uVar13 = (ulong)local_34;
    uVar6 = std::vector<unsigned_char,std::allocator<unsigned_char>>::size();
    if (uVar6 <= uVar13) break;
    for (local_38 = 0; local_38 < 300; local_38 = local_38 + 1) {
      pbVar9 = (byte *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                                 (local_b8,(long)local_34);
      bVar2 = *pbVar9;
      iVar5 = local_38 << 5;
      pcVar11 = (char *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                                  (local_b8,(long)(local_34 + -5));
      cVar3 = *pcVar11;
      pbVar9 = (byte *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                                 (local_b8,(long)local_34);
      *pbVar9 = cVar3 == 'n' ^ bVar2 ^ (byte)iVar5;
    }
    local_34 = local_34 + 1;
  }
  std::allocator<char>::allocator();
                    // try { // try from 00401ddb to 00401ddf has its CatchHandler @ 00401f1e
  std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
  basic_string<std::allocator<char>>
            (local_d8,"flag{ph3w...u finaLly g0t it! jump into cell wHen U g3t t0 the next cha11}",
             &local_41);
  std::allocator<char>::~allocator((allocator<char> *)&local_41);
  tVar10 = time((time_t *)0x0);
  srand((uint)tVar10);
  local_3c = 0;
  do {
    uVar13 = (ulong)local_3c;
    uVar6 = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::size();
    if (uVar6 <= uVar13) {
      pbVar12 = std::operator<<((basic_ostream *)std::cout,"You are worthy!");
      std::basic_ostream<char,std::char_traits<char>>::operator<<
                ((basic_ostream<char,std::char_traits<char>> *)pbVar12,
                 std::endl<char,std::char_traits<char>>);
LAB_00401ee4:
      std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string
                (local_d8);
      std::vector<unsigned_char,std::allocator<unsigned_char>>::~vector(local_b8);
      return;
    }
                    // try { // try from 00401e1c to 00401ee2 has its CatchHandler @ 00401f2f
    pcVar11 = (char *)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
                      operator[]((ulong)local_d8);
    cVar3 = *pcVar11;
    pcVar11 = (char *)std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
                                (local_b8,(long)local_3c);
    if (cVar3 != *pcVar11) {
      local_40 = rand();
      pbVar12 = std::operator<<((basic_ostream *)std::cout,fail_msgs + (long)(local_40 % 6) * 0x80);
      std::basic_ostream<char,std::char_traits<char>>::operator<<
                ((basic_ostream<char,std::char_traits<char>> *)pbVar12,
                 std::endl<char,std::char_traits<char>>);
      goto LAB_00401ee4;
    }
    local_3c = local_3c + 1;
  } while( true );
}



bool main(int param_1,char **param_2)

{
  basic_ostream *pbVar1;
  basic_string<char,std::char_traits<char>,std::allocator<char>> local_68 [47];
  allocator local_39;
  basic_string local_38 [10];
  
  if (param_1 < 2) {
    pbVar1 = std::operator<<((basic_ostream *)std::cout,"Usage: ");
    pbVar1 = std::operator<<(pbVar1,*param_2);
    pbVar1 = std::operator<<(pbVar1," <food>");
    std::basic_ostream<char,std::char_traits<char>>::operator<<
              ((basic_ostream<char,std::char_traits<char>> *)pbVar1,
               std::endl<char,std::char_traits<char>>);
  }
  else {
    std::allocator<char>::allocator();
                    // try { // try from 00401ff1 to 00401ff5 has its CatchHandler @ 00402040
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
    basic_string<std::allocator<char>>(local_68,param_2[1],&local_39);
    std::allocator<char>::~allocator((allocator<char> *)&local_39);
                    // try { // try from 00402010 to 00402014 has its CatchHandler @ 0040206b
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::basic_string
              (local_38);
                    // try { // try from 0040201c to 00402020 has its CatchHandler @ 0040205a
    verify((basic_string)local_38);
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string
              ((basic_string<char,std::char_traits<char>,std::allocator<char>> *)local_38);
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string
              (local_68);
  }
  return param_1 < 2;
}



// __static_initialization_and_destruction_0(int, int)

void __static_initialization_and_destruction_0(int param_1,int param_2)

{
  allocator local_36d8 [13999];
  allocator<int> local_29 [9];
  
  if ((param_1 == 1) && (param_2 == 0xffff)) {
    std::ios_base::Init::Init((Init *)&std::__ioinit);
    __cxa_atexit(std::ios_base::Init::~Init,&std::__ioinit,&__dso_handle);
    memcpy(local_36d8,&DAT_00403740,0x36a4);
    std::allocator<int>::allocator();
                    // try { // try from 00402135 to 00402139 has its CatchHandler @ 0040215c
    std::vector<int,std::allocator<int>>::vector(0x409df0,local_36d8);
    std::allocator<int>::~allocator(local_29);
    __cxa_atexit(std::vector<int,std::allocator<int>>::~vector,data,&__dso_handle);
  }
  return;
}



void _GLOBAL__sub_I_fail_msgs(void)

{
  __static_initialization_and_destruction_0(1,0xffff);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__is_constant_evaluated()

undefined8 std::__is_constant_evaluated(void)

{
  return 0;
}



// std::char_traits<char>::length(char const*)

void std::char_traits<char>::length(char *param_1)

{
  char cVar1;
  
  cVar1 = __is_constant_evaluated();
  if (cVar1 == '\0') {
    strlen(param_1);
  }
  else {
    __gnu_cxx::char_traits<char>::length(param_1);
  }
  return;
}



// __gnu_cxx::char_traits<char>::length(char const*)

long __gnu_cxx::char_traits<char>::length(char *param_1)

{
  char cVar1;
  char local_11;
  long local_10;
  
  local_10 = 0;
  while( true ) {
    local_11 = '\0';
    cVar1 = eq(param_1 + local_10,&local_11);
    if (cVar1 == '\x01') break;
    local_10 = local_10 + 1;
  }
  return local_10;
}



// std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>
// >::_Alloc_hider::~_Alloc_hider()

void __thiscall
std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_Alloc_hider::
~_Alloc_hider(_Alloc_hider *this)

{
  std::allocator<char>::~allocator((allocator<char> *)this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::allocator<int>::allocator()

void std::allocator<int>::allocator(void)

{
  __new_allocator<int>::__new_allocator();
  return;
}



// std::allocator<int>::~allocator()

void __thiscall std::allocator<int>::~allocator(allocator<int> *this)

{
  __new_allocator<int>::~__new_allocator((__new_allocator<int> *)this);
  return;
}



// std::vector<int, std::allocator<int> >::vector(std::initializer_list<int>, std::allocator<int>
// const&)

void std::vector<int,std::allocator<int>>::vector(initializer_list param_1,allocator *param_2)

{
  forward_iterator_tag fVar1;
  int *piVar2;
  allocator *in_RCX;
  undefined4 in_register_0000003c;
  
  _Vector_base<int,std::allocator<int>>::_Vector_base
            ((_Vector_base<int,std::allocator<int>> *)(int *)CONCAT44(in_register_0000003c,param_1),
             in_RCX);
  fVar1 = initializer_list<int>::end();
  piVar2 = (int *)initializer_list<int>::begin();
                    // try { // try from 004022d0 to 004022d4 has its CatchHandler @ 004022d7
  _M_range_initialize<int_const*>((int *)CONCAT44(in_register_0000003c,param_1),piVar2,fVar1);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::allocator<unsigned char>::allocator()

void std::allocator<unsigned_char>::allocator(void)

{
  __new_allocator<unsigned_char>::__new_allocator();
  return;
}



// std::allocator<unsigned char>::~allocator()

void __thiscall std::allocator<unsigned_char>::~allocator(allocator<unsigned_char> *this)

{
  __new_allocator<unsigned_char>::~__new_allocator((__new_allocator<unsigned_char> *)this);
  return;
}



// std::vector<unsigned char, std::allocator<unsigned char> >::vector(std::initializer_list<unsigned
// char>, std::allocator<unsigned char> const&)

void std::vector<unsigned_char,std::allocator<unsigned_char>>::vector
               (initializer_list param_1,allocator *param_2)

{
  forward_iterator_tag fVar1;
  uchar *puVar2;
  allocator *in_RCX;
  undefined4 in_register_0000003c;
  
  _Vector_base<unsigned_char,std::allocator<unsigned_char>>::_Vector_base
            ((_Vector_base<unsigned_char,std::allocator<unsigned_char>> *)
             CONCAT44(in_register_0000003c,param_1),in_RCX);
  fVar1 = initializer_list<unsigned_char>::end();
  puVar2 = (uchar *)initializer_list<unsigned_char>::begin();
                    // try { // try from 00402390 to 00402394 has its CatchHandler @ 00402397
  _M_range_initialize<unsigned_char_const*>
            ((uchar *)(_Vector_base<unsigned_char,std::allocator<unsigned_char>> *)
                      CONCAT44(in_register_0000003c,param_1),puVar2,fVar1);
  return;
}



// std::vector<unsigned char, std::allocator<unsigned char> >::~vector()

void __thiscall
std::vector<unsigned_char,std::allocator<unsigned_char>>::~vector
          (vector<unsigned_char,std::allocator<unsigned_char>> *this)

{
  allocator *paVar1;
  
  paVar1 = (allocator *)
           _Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_get_Tp_allocator();
  _Destroy<unsigned_char*,unsigned_char>(*(uchar **)this,*(uchar **)(this + 8),paVar1);
  _Vector_base<unsigned_char,std::allocator<unsigned_char>>::~_Vector_base
            ((_Vector_base<unsigned_char,std::allocator<unsigned_char>> *)this);
  return;
}



// std::vector<unsigned char, std::allocator<unsigned char> >::operator[](unsigned long)

long __thiscall
std::vector<unsigned_char,std::allocator<unsigned_char>>::operator[]
          (vector<unsigned_char,std::allocator<unsigned_char>> *this,ulong param_1)

{
  return param_1 + *(long *)this;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::vector<unsigned char, std::allocator<unsigned char> >::size() const

long std::vector<unsigned_char,std::allocator<unsigned_char>>::size(void)

{
  long *in_RDI;
  
  return in_RDI[1] - *in_RDI;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::vector<int, std::allocator<int> >::size() const

long std::vector<int,std::allocator<int>>::size(void)

{
  long *in_RDI;
  
  return in_RDI[1] - *in_RDI >> 2;
}



// std::vector<int, std::allocator<int> >::operator[](unsigned long)

long __thiscall
std::vector<int,std::allocator<int>>::operator[]
          (vector<int,std::allocator<int>> *this,ulong param_1)

{
  return *(long *)this + param_1 * 4;
}



// std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>
// >::basic_string<std::allocator<char> >(char const*, std::allocator<char> const&)

void __thiscall
std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
basic_string<std::allocator<char>>
          (basic_string<char,std::char_traits<char>,std::allocator<char>> *this,char *param_1,
          allocator *param_2)

{
  int iVar1;
  char *pcVar2;
  
  pcVar2 = (char *)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
                   _M_local_data();
  std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_Alloc_hider::
  _Alloc_hider((_Alloc_hider *)this,pcVar2,param_2);
  if (param_1 == (char *)0x0) {
                    // try { // try from 004024c2 to 004024f4 has its CatchHandler @ 004024f7
    std::__throw_logic_error("basic_string: construction from null is not valid");
  }
  iVar1 = char_traits<char>::length(param_1);
  _M_construct<char_const*>((char *)this,param_1,iVar1 + (int)param_1);
  return;
}



// __gnu_cxx::char_traits<char>::eq(char const&, char const&)

bool __gnu_cxx::char_traits<char>::eq(char *param_1,char *param_2)

{
  return *param_1 == *param_2;
}



// std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>
// >::_M_construct<char const*>(char const*, char const*,
// std::forward_iterator_tag)::_Guard::_Guard(std::__cxx11::basic_string<char,
// std::char_traits<char>, std::allocator<char> >*)

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
     _M_construct<char_const*>(char_const*,char_const*,std::forward_iterator_tag)::_Guard::
     _Guard(std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>_>__
               (undefined8 *param_1,undefined8 param_2)

{
  *param_1 = param_2;
  return;
}



// ~_Guard()

void __thiscall
std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
_M_construct<char_const*>(char_const*,char_const*,std::forward_iterator_tag)::_Guard::~_Guard
          (_Guard *this)

{
  if (*(long *)this != 0) {
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_dispose();
  }
  return;
}



// void std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>
// >::_M_construct<char const*>(char const*, char const*, std::forward_iterator_tag)

void std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
     _M_construct<char_const*>(char *param_1,char *param_2,forward_iterator_tag param_3)

{
  difference_type dVar1;
  undefined4 extraout_var;
  char *pcVar2;
  undefined4 in_register_00000014;
  undefined8 local_20;
  ulong local_18;
  char *local_10;
  
  dVar1 = distance<char_const*>(param_2,(char *)CONCAT44(in_register_00000014,param_3));
  local_18 = CONCAT44(extraout_var,dVar1);
  if (local_18 < 0x10) {
    local_10 = param_1;
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_local_data();
  }
  else {
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_create
              ((ulong *)param_1,(ulong)&local_18);
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_data(param_1);
    std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_capacity
              ((ulong)param_1);
  }
  basic_string<char,std::char_traits<char>,std::allocator<char>>::
  _M_construct<char_const*>(char_const*,char_const*,std::forward_iterator_tag)::_Guard::_Guard(std::
  __cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>_>__(&local_20,param_1);
  pcVar2 = (char *)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::
                   _M_data();
  std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_S_copy_chars
            (pcVar2,param_2,(char *)CONCAT44(in_register_00000014,param_3));
  local_20 = 0;
  std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::_M_set_length
            ((ulong)param_1);
  _M_construct<char_const*>(char_const*,char_const*,std::forward_iterator_tag)::_Guard::~_Guard
            ((_Guard *)&local_20);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__new_allocator<int>::__new_allocator()

void std::__new_allocator<int>::__new_allocator(void)

{
  return;
}



// std::__new_allocator<int>::~__new_allocator()

void __thiscall std::__new_allocator<int>::~__new_allocator(__new_allocator<int> *this)

{
  return;
}



// std::_Vector_base<int, std::allocator<int> >::_Vector_impl::~_Vector_impl()

void __thiscall
std::_Vector_base<int,std::allocator<int>>::_Vector_impl::~_Vector_impl(_Vector_impl *this)

{
  allocator<int>::~allocator((allocator<int> *)this);
  return;
}



// std::_Vector_base<int, std::allocator<int> >::_Vector_base(std::allocator<int> const&)

void __thiscall
std::_Vector_base<int,std::allocator<int>>::_Vector_base
          (_Vector_base<int,std::allocator<int>> *this,allocator *param_1)

{
  _Vector_impl::_Vector_impl((_Vector_impl *)this,param_1);
  return;
}



// std::_Vector_base<int, std::allocator<int> >::~_Vector_base()

void __thiscall
std::_Vector_base<int,std::allocator<int>>::~_Vector_base
          (_Vector_base<int,std::allocator<int>> *this)

{
  _M_deallocate(this,*(int **)this,*(long *)(this + 0x10) - *(long *)this >> 2);
  _Vector_impl::~_Vector_impl((_Vector_impl *)this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::initializer_list<int>::begin() const

undefined8 std::initializer_list<int>::begin(void)

{
  undefined8 *in_RDI;
  
  return *in_RDI;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::initializer_list<int>::end() const

long std::initializer_list<int>::end(void)

{
  long lVar1;
  long lVar2;
  
  lVar1 = begin();
  lVar2 = size();
  return lVar2 * 4 + lVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<int const*>::difference_type std::distance<int const*>(int const*, int
// const*)

difference_type std::distance<int_const*>(int *param_1,int *param_2)

{
  difference_type dVar1;
  int *local_10;
  
  local_10 = param_1;
  __iterator_category<int_const*>(&local_10);
  dVar1 = __distance<int_const*>(local_10,param_2,(random_access_iterator_tag)param_2);
  return dVar1;
}



// void std::vector<int, std::allocator<int> >::_M_range_initialize<int const*>(int const*, int
// const*, std::forward_iterator_tag)

void std::vector<int,std::allocator<int>>::_M_range_initialize<int_const*>
               (int *param_1,int *param_2,forward_iterator_tag param_3)

{
  difference_type dVar1;
  undefined4 extraout_var;
  allocator *paVar2;
  ulong uVar3;
  undefined8 uVar4;
  int *piVar5;
  undefined4 in_register_00000014;
  
  dVar1 = distance<int_const*>(param_2,(int *)CONCAT44(in_register_00000014,param_3));
  paVar2 = (allocator *)_Vector_base<int,std::allocator<int>>::_M_get_Tp_allocator();
  uVar3 = _S_check_init_len(CONCAT44(extraout_var,dVar1),paVar2);
  uVar4 = _Vector_base<int,std::allocator<int>>::_M_allocate
                    ((_Vector_base<int,std::allocator<int>> *)param_1,uVar3);
  *(undefined8 *)param_1 = uVar4;
  *(ulong *)(param_1 + 4) = CONCAT44(extraout_var,dVar1) * 4 + *(long *)param_1;
  paVar2 = (allocator *)_Vector_base<int,std::allocator<int>>::_M_get_Tp_allocator();
  piVar5 = __uninitialized_copy_a<int_const*,int*,int>
                     (param_2,(int *)CONCAT44(in_register_00000014,param_3),*(int **)param_1,paVar2)
  ;
  *(int **)(param_1 + 2) = piVar5;
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__new_allocator<unsigned char>::__new_allocator()

void std::__new_allocator<unsigned_char>::__new_allocator(void)

{
  return;
}



// std::__new_allocator<unsigned char>::~__new_allocator()

void __thiscall
std::__new_allocator<unsigned_char>::~__new_allocator(__new_allocator<unsigned_char> *this)

{
  return;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char> >::_Vector_impl::~_Vector_impl()

void __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_Vector_impl::~_Vector_impl
          (_Vector_impl *this)

{
  allocator<unsigned_char>::~allocator((allocator<unsigned_char> *)this);
  return;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char>
// >::_Vector_base(std::allocator<unsigned char> const&)

void __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_Vector_base
          (_Vector_base<unsigned_char,std::allocator<unsigned_char>> *this,allocator *param_1)

{
  _Vector_impl::_Vector_impl((_Vector_impl *)this,param_1);
  return;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char> >::~_Vector_base()

void __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::~_Vector_base
          (_Vector_base<unsigned_char,std::allocator<unsigned_char>> *this)

{
  _M_deallocate(this,*(uchar **)this,*(long *)(this + 0x10) - *(long *)this);
  _Vector_impl::~_Vector_impl((_Vector_impl *)this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::initializer_list<unsigned char>::begin() const

undefined8 std::initializer_list<unsigned_char>::begin(void)

{
  undefined8 *in_RDI;
  
  return *in_RDI;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::initializer_list<unsigned char>::end() const

long std::initializer_list<unsigned_char>::end(void)

{
  long lVar1;
  long lVar2;
  
  lVar1 = begin();
  lVar2 = size();
  return lVar2 + lVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<unsigned char const*>::difference_type std::distance<unsigned char
// const*>(unsigned char const*, unsigned char const*)

difference_type std::distance<unsigned_char_const*>(uchar *param_1,uchar *param_2)

{
  difference_type dVar1;
  uchar *local_10;
  
  local_10 = param_1;
  __iterator_category<unsigned_char_const*>(&local_10);
  dVar1 = __distance<unsigned_char_const*>(local_10,param_2,(random_access_iterator_tag)param_2);
  return dVar1;
}



// void std::vector<unsigned char, std::allocator<unsigned char> >::_M_range_initialize<unsigned
// char const*>(unsigned char const*, unsigned char const*, std::forward_iterator_tag)

void std::vector<unsigned_char,std::allocator<unsigned_char>>::
     _M_range_initialize<unsigned_char_const*>
               (uchar *param_1,uchar *param_2,forward_iterator_tag param_3)

{
  difference_type dVar1;
  undefined4 extraout_var;
  allocator *paVar2;
  ulong uVar3;
  undefined8 uVar4;
  uchar *puVar5;
  undefined4 in_register_00000014;
  
  dVar1 = distance<unsigned_char_const*>(param_2,(uchar *)CONCAT44(in_register_00000014,param_3));
  paVar2 = (allocator *)
           _Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_get_Tp_allocator();
  uVar3 = _S_check_init_len(CONCAT44(extraout_var,dVar1),paVar2);
  uVar4 = _Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_allocate
                    ((_Vector_base<unsigned_char,std::allocator<unsigned_char>> *)param_1,uVar3);
  *(undefined8 *)param_1 = uVar4;
  *(ulong *)(param_1 + 0x10) = *(long *)param_1 + CONCAT44(extraout_var,dVar1);
  paVar2 = (allocator *)
           _Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_get_Tp_allocator();
  puVar5 = __uninitialized_copy_a<unsigned_char_const*,unsigned_char*,unsigned_char>
                     (param_2,(uchar *)CONCAT44(in_register_00000014,param_3),*(uchar **)param_1,
                      paVar2);
  *(uchar **)(param_1 + 8) = puVar5;
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::_Vector_base<unsigned char, std::allocator<unsigned char> >::_M_get_Tp_allocator()

undefined8 std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_get_Tp_allocator(void)

{
  undefined8 in_RDI;
  
  return in_RDI;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// void std::_Destroy<unsigned char*, unsigned char>(unsigned char*, unsigned char*,
// std::allocator<unsigned char>&)

void std::_Destroy<unsigned_char*,unsigned_char>(uchar *param_1,uchar *param_2,allocator *param_3)

{
  _Destroy<unsigned_char*>(param_1,param_2);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<char const*>::difference_type std::distance<char const*>(char const*, char
// const*)

difference_type std::distance<char_const*>(char *param_1,char *param_2)

{
  difference_type dVar1;
  char *local_10;
  
  local_10 = param_1;
  __iterator_category<char_const*>(&local_10);
  dVar1 = __distance<char_const*>(local_10,param_2,(random_access_iterator_tag)param_2);
  return dVar1;
}



// std::_Vector_base<int, std::allocator<int> >::_Vector_impl::_Vector_impl(std::allocator<int>
// const&)

void __thiscall
std::_Vector_base<int,std::allocator<int>>::_Vector_impl::_Vector_impl
          (_Vector_impl *this,allocator *param_1)

{
  allocator<int>::allocator((allocator *)this);
  _Vector_impl_data::_Vector_impl_data((_Vector_impl_data *)this);
  return;
}



// std::_Vector_base<int, std::allocator<int> >::_M_deallocate(int*, unsigned long)

void __thiscall
std::_Vector_base<int,std::allocator<int>>::_M_deallocate
          (_Vector_base<int,std::allocator<int>> *this,int *param_1,ulong param_2)

{
  if (param_1 != (int *)0x0) {
    allocator_traits<std::allocator<int>>::deallocate((allocator *)this,param_1,param_2);
  }
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::initializer_list<int>::size() const

undefined8 std::initializer_list<int>::size(void)

{
  long in_RDI;
  
  return *(undefined8 *)(in_RDI + 8);
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<int const*>::iterator_category std::__iterator_category<int const*>(int
// const* const&)

iterator_category std::__iterator_category<int_const*>(int **param_1)

{
  iterator_category in_EAX;
  
  return in_EAX;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<int const*>::difference_type std::__distance<int const*>(int const*, int
// const*, std::random_access_iterator_tag)

difference_type
std::__distance<int_const*>(int *param_1,int *param_2,random_access_iterator_tag param_3)

{
  return (difference_type)((long)param_2 - (long)param_1 >> 2);
}



// std::vector<int, std::allocator<int> >::_S_check_init_len(unsigned long, std::allocator<int>
// const&)

ulong std::vector<int,std::allocator<int>>::_S_check_init_len(ulong param_1,allocator *param_2)

{
  ulong uVar1;
  allocator local_19 [9];
  
  allocator<int>::allocator(local_19);
  uVar1 = _S_max_size(local_19);
  allocator<int>::~allocator((allocator<int> *)local_19);
  if (uVar1 < param_1) {
    std::__throw_length_error("cannot create std::vector larger than max_size()");
  }
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::_Vector_base<int, std::allocator<int> >::_M_get_Tp_allocator()

undefined8 std::_Vector_base<int,std::allocator<int>>::_M_get_Tp_allocator(void)

{
  undefined8 in_RDI;
  
  return in_RDI;
}



// std::_Vector_base<int, std::allocator<int> >::_M_allocate(unsigned long)

undefined8 __thiscall
std::_Vector_base<int,std::allocator<int>>::_M_allocate
          (_Vector_base<int,std::allocator<int>> *this,ulong param_1)

{
  undefined8 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = allocator_traits<std::allocator<int>>::allocate((allocator *)this,param_1);
  }
  return uVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::__uninitialized_copy_a<int const*, int*, int>(int const*, int const*, int*,
// std::allocator<int>&)

int * std::__uninitialized_copy_a<int_const*,int*,int>
                (int *param_1,int *param_2,int *param_3,allocator *param_4)

{
  int *piVar1;
  
  piVar1 = uninitialized_copy<int_const*,int*>(param_1,param_2,param_3);
  return piVar1;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char>
// >::_Vector_impl::_Vector_impl(std::allocator<unsigned char> const&)

void __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_Vector_impl::_Vector_impl
          (_Vector_impl *this,allocator *param_1)

{
  allocator<unsigned_char>::allocator((allocator *)this);
  _Vector_impl_data::_Vector_impl_data((_Vector_impl_data *)this);
  return;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char> >::_M_deallocate(unsigned char*,
// unsigned long)

void __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_deallocate
          (_Vector_base<unsigned_char,std::allocator<unsigned_char>> *this,uchar *param_1,
          ulong param_2)

{
  if (param_1 != (uchar *)0x0) {
    allocator_traits<std::allocator<unsigned_char>>::deallocate((allocator *)this,param_1,param_2);
  }
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::initializer_list<unsigned char>::size() const

undefined8 std::initializer_list<unsigned_char>::size(void)

{
  long in_RDI;
  
  return *(undefined8 *)(in_RDI + 8);
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<unsigned char const*>::iterator_category std::__iterator_category<unsigned
// char const*>(unsigned char const* const&)

iterator_category std::__iterator_category<unsigned_char_const*>(uchar **param_1)

{
  iterator_category in_EAX;
  
  return in_EAX;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<unsigned char const*>::difference_type std::__distance<unsigned char
// const*>(unsigned char const*, unsigned char const*, std::random_access_iterator_tag)

difference_type
std::__distance<unsigned_char_const*>
          (uchar *param_1,uchar *param_2,random_access_iterator_tag param_3)

{
  return (int)param_2 - (int)param_1;
}



// std::vector<unsigned char, std::allocator<unsigned char> >::_S_check_init_len(unsigned long,
// std::allocator<unsigned char> const&)

ulong std::vector<unsigned_char,std::allocator<unsigned_char>>::_S_check_init_len
                (ulong param_1,allocator *param_2)

{
  ulong uVar1;
  allocator local_19 [9];
  
  allocator<unsigned_char>::allocator(local_19);
  uVar1 = _S_max_size(local_19);
  allocator<unsigned_char>::~allocator((allocator<unsigned_char> *)local_19);
  if (uVar1 < param_1) {
    std::__throw_length_error("cannot create std::vector larger than max_size()");
  }
  return param_1;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char> >::_M_allocate(unsigned long)

undefined8 __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_M_allocate
          (_Vector_base<unsigned_char,std::allocator<unsigned_char>> *this,ulong param_1)

{
  undefined8 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = allocator_traits<std::allocator<unsigned_char>>::allocate((allocator *)this,param_1);
  }
  return uVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::__uninitialized_copy_a<unsigned char const*, unsigned char*, unsigned
// char>(unsigned char const*, unsigned char const*, unsigned char*, std::allocator<unsigned char>&)

uchar * std::__uninitialized_copy_a<unsigned_char_const*,unsigned_char*,unsigned_char>
                  (uchar *param_1,uchar *param_2,uchar *param_3,allocator *param_4)

{
  uchar *puVar1;
  
  puVar1 = uninitialized_copy<unsigned_char_const*,unsigned_char*>(param_1,param_2,param_3);
  return puVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// void std::_Destroy<unsigned char*>(unsigned char*, unsigned char*)

void std::_Destroy<unsigned_char*>(uchar *param_1,uchar *param_2)

{
  _Destroy_aux<true>::__destroy<unsigned_char*>(param_1,param_2);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<char const*>::iterator_category std::__iterator_category<char const*>(char
// const* const&)

iterator_category std::__iterator_category<char_const*>(char **param_1)

{
  iterator_category in_EAX;
  
  return in_EAX;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::iterator_traits<char const*>::difference_type std::__distance<char const*>(char const*, char
// const*, std::random_access_iterator_tag)

difference_type
std::__distance<char_const*>(char *param_1,char *param_2,random_access_iterator_tag param_3)

{
  return (int)param_2 - (int)param_1;
}



// std::allocator<int>::allocator(std::allocator<int> const&)

void std::allocator<int>::allocator(allocator *param_1)

{
  __new_allocator<int>::__new_allocator((__new_allocator *)param_1);
  return;
}



// std::_Vector_base<int, std::allocator<int> >::_Vector_impl_data::_Vector_impl_data()

void __thiscall
std::_Vector_base<int,std::allocator<int>>::_Vector_impl_data::_Vector_impl_data
          (_Vector_impl_data *this)

{
  *(undefined8 *)this = 0;
  *(undefined8 *)(this + 8) = 0;
  *(undefined8 *)(this + 0x10) = 0;
  return;
}



// std::allocator_traits<std::allocator<int> >::deallocate(std::allocator<int>&, int*, unsigned
// long)

void std::allocator_traits<std::allocator<int>>::deallocate
               (allocator *param_1,int *param_2,ulong param_3)

{
  __new_allocator<int>::deallocate((__new_allocator<int> *)param_1,param_2,param_3);
  return;
}



// std::vector<int, std::allocator<int> >::_S_max_size(std::allocator<int> const&)

ulong std::vector<int,std::allocator<int>>::_S_max_size(allocator *param_1)

{
  ulong *puVar1;
  ulong local_18;
  ulong local_10;
  
  local_10 = 0x1fffffffffffffff;
  local_18 = allocator_traits<std::allocator<int>>::max_size(param_1);
  puVar1 = min<unsigned_long>(&local_10,&local_18);
  return *puVar1;
}



// std::allocator_traits<std::allocator<int> >::allocate(std::allocator<int>&, unsigned long)

void std::allocator_traits<std::allocator<int>>::allocate(allocator *param_1,ulong param_2)

{
  __new_allocator<int>::allocate((ulong)param_1,(void *)param_2);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::uninitialized_copy<int const*, int*>(int const*, int const*, int*)

int * std::uninitialized_copy<int_const*,int*>(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  
  piVar1 = __uninitialized_copy<true>::__uninit_copy<int_const*,int*>(param_1,param_2,param_3);
  return piVar1;
}



// std::allocator<unsigned char>::allocator(std::allocator<unsigned char> const&)

void std::allocator<unsigned_char>::allocator(allocator *param_1)

{
  __new_allocator<unsigned_char>::__new_allocator((__new_allocator *)param_1);
  return;
}



// std::_Vector_base<unsigned char, std::allocator<unsigned char>
// >::_Vector_impl_data::_Vector_impl_data()

void __thiscall
std::_Vector_base<unsigned_char,std::allocator<unsigned_char>>::_Vector_impl_data::_Vector_impl_data
          (_Vector_impl_data *this)

{
  *(undefined8 *)this = 0;
  *(undefined8 *)(this + 8) = 0;
  *(undefined8 *)(this + 0x10) = 0;
  return;
}



// std::allocator_traits<std::allocator<unsigned char> >::deallocate(std::allocator<unsigned char>&,
// unsigned char*, unsigned long)

void std::allocator_traits<std::allocator<unsigned_char>>::deallocate
               (allocator *param_1,uchar *param_2,ulong param_3)

{
  __new_allocator<unsigned_char>::deallocate
            ((__new_allocator<unsigned_char> *)param_1,param_2,param_3);
  return;
}



// std::vector<unsigned char, std::allocator<unsigned char> >::_S_max_size(std::allocator<unsigned
// char> const&)

ulong std::vector<unsigned_char,std::allocator<unsigned_char>>::_S_max_size(allocator *param_1)

{
  ulong *puVar1;
  ulong local_18;
  ulong local_10;
  
  local_10 = 0x7fffffffffffffff;
  local_18 = allocator_traits<std::allocator<unsigned_char>>::max_size(param_1);
  puVar1 = min<unsigned_long>(&local_10,&local_18);
  return *puVar1;
}



// std::allocator_traits<std::allocator<unsigned char> >::allocate(std::allocator<unsigned char>&,
// unsigned long)

void std::allocator_traits<std::allocator<unsigned_char>>::allocate
               (allocator *param_1,ulong param_2)

{
  __new_allocator<unsigned_char>::allocate((ulong)param_1,(void *)param_2);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::uninitialized_copy<unsigned char const*, unsigned char*>(unsigned char
// const*, unsigned char const*, unsigned char*)

uchar * std::uninitialized_copy<unsigned_char_const*,unsigned_char*>
                  (uchar *param_1,uchar *param_2,uchar *param_3)

{
  uchar *puVar1;
  
  puVar1 = __uninitialized_copy<true>::__uninit_copy<unsigned_char_const*,unsigned_char*>
                     (param_1,param_2,param_3);
  return puVar1;
}



// void std::_Destroy_aux<true>::__destroy<unsigned char*>(unsigned char*, unsigned char*)

void std::_Destroy_aux<true>::__destroy<unsigned_char*>(uchar *param_1,uchar *param_2)

{
  return;
}



// std::__new_allocator<int>::__new_allocator(std::__new_allocator<int> const&)

void std::__new_allocator<int>::__new_allocator(__new_allocator *param_1)

{
  return;
}



// std::__new_allocator<int>::deallocate(int*, unsigned long)

void __thiscall
std::__new_allocator<int>::deallocate(__new_allocator<int> *this,int *param_1,ulong param_2)

{
  operator_delete(param_1,param_2 * 4);
  return;
}



// std::allocator_traits<std::allocator<int> >::max_size(std::allocator<int> const&)

void std::allocator_traits<std::allocator<int>>::max_size(allocator *param_1)

{
  __new_allocator<int>::max_size();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned long const& std::min<unsigned long>(unsigned long const&, unsigned long const&)

ulong * std::min<unsigned_long>(ulong *param_1,ulong *param_2)

{
  if (*param_2 < *param_1) {
    param_1 = param_2;
  }
  return param_1;
}



// std::__new_allocator<int>::allocate(unsigned long, void const*)

void std::__new_allocator<int>::allocate(ulong param_1,void *param_2)

{
  void *pvVar1;
  
  pvVar1 = (void *)_M_max_size();
  if (pvVar1 < param_2) {
    if ((void *)0x3fffffffffffffff < param_2) {
      std::__throw_bad_array_new_length();
    }
    std::__throw_bad_alloc();
  }
  operator_new((long)param_2 << 2);
  return;
}



// int* std::__uninitialized_copy<true>::__uninit_copy<int const*, int*>(int const*, int const*,
// int*)

int * std::__uninitialized_copy<true>::__uninit_copy<int_const*,int*>
                (int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  
  piVar1 = copy<int_const*,int*>(param_1,param_2,param_3);
  return piVar1;
}



// std::__new_allocator<unsigned char>::__new_allocator(std::__new_allocator<unsigned char> const&)

void std::__new_allocator<unsigned_char>::__new_allocator(__new_allocator *param_1)

{
  return;
}



// std::__new_allocator<unsigned char>::deallocate(unsigned char*, unsigned long)

void __thiscall
std::__new_allocator<unsigned_char>::deallocate
          (__new_allocator<unsigned_char> *this,uchar *param_1,ulong param_2)

{
  operator_delete(param_1,param_2);
  return;
}



// std::allocator_traits<std::allocator<unsigned char> >::max_size(std::allocator<unsigned char>
// const&)

void std::allocator_traits<std::allocator<unsigned_char>>::max_size(allocator *param_1)

{
  __new_allocator<unsigned_char>::max_size();
  return;
}



// std::__new_allocator<unsigned char>::allocate(unsigned long, void const*)

void std::__new_allocator<unsigned_char>::allocate(ulong param_1,void *param_2)

{
  void *pvVar1;
  
  pvVar1 = (void *)_M_max_size();
  if (pvVar1 < param_2) {
    std::__throw_bad_alloc();
  }
  operator_new((ulong)param_2);
  return;
}



// unsigned char* std::__uninitialized_copy<true>::__uninit_copy<unsigned char const*, unsigned
// char*>(unsigned char const*, unsigned char const*, unsigned char*)

uchar * std::__uninitialized_copy<true>::__uninit_copy<unsigned_char_const*,unsigned_char*>
                  (uchar *param_1,uchar *param_2,uchar *param_3)

{
  uchar *puVar1;
  
  puVar1 = copy<unsigned_char_const*,unsigned_char*>(param_1,param_2,param_3);
  return puVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__new_allocator<int>::max_size() const

void std::__new_allocator<int>::max_size(void)

{
  _M_max_size();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__new_allocator<int>::_M_max_size() const

undefined8 std::__new_allocator<int>::_M_max_size(void)

{
  return 0x1fffffffffffffff;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::copy<int const*, int*>(int const*, int const*, int*)

int * std::copy<int_const*,int*>(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  int *piVar2;
  
  piVar1 = __miter_base<int_const*>(param_2);
  piVar2 = __miter_base<int_const*>(param_1);
  piVar1 = __copy_move_a<false,int_const*,int*>(piVar2,piVar1,param_3);
  return piVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__new_allocator<unsigned char>::max_size() const

void std::__new_allocator<unsigned_char>::max_size(void)

{
  _M_max_size();
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// std::__new_allocator<unsigned char>::_M_max_size() const

undefined8 std::__new_allocator<unsigned_char>::_M_max_size(void)

{
  return 0x7fffffffffffffff;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::copy<unsigned char const*, unsigned char*>(unsigned char const*, unsigned
// char const*, unsigned char*)

uchar * std::copy<unsigned_char_const*,unsigned_char*>(uchar *param_1,uchar *param_2,uchar *param_3)

{
  uchar *puVar1;
  uchar *puVar2;
  
  puVar1 = __miter_base<unsigned_char_const*>(param_2);
  puVar2 = __miter_base<unsigned_char_const*>(param_1);
  puVar1 = __copy_move_a<false,unsigned_char_const*,unsigned_char*>(puVar2,puVar1,param_3);
  return puVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int const* std::__miter_base<int const*>(int const*)

int * std::__miter_base<int_const*>(int *param_1)

{
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::__copy_move_a<false, int const*, int*>(int const*, int const*, int*)

int * std::__copy_move_a<false,int_const*,int*>(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *local_30;
  int *local_28;
  int *local_20;
  
  local_30 = param_3;
  local_28 = param_2;
  local_20 = param_1;
  piVar1 = __niter_base<int*>(param_3);
  piVar2 = __niter_base<int_const*>(local_28);
  piVar3 = __niter_base<int_const*>(local_20);
  piVar1 = __copy_move_a1<false,int_const*,int*>(piVar3,piVar2,piVar1);
  piVar1 = __niter_wrap<int*>(&local_30,piVar1);
  return piVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char const* std::__miter_base<unsigned char const*>(unsigned char const*)

uchar * std::__miter_base<unsigned_char_const*>(uchar *param_1)

{
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::__copy_move_a<false, unsigned char const*, unsigned char*>(unsigned char
// const*, unsigned char const*, unsigned char*)

uchar * std::__copy_move_a<false,unsigned_char_const*,unsigned_char*>
                  (uchar *param_1,uchar *param_2,uchar *param_3)

{
  uchar *puVar1;
  uchar *puVar2;
  uchar *puVar3;
  uchar *local_30;
  uchar *local_28;
  uchar *local_20;
  
  local_30 = param_3;
  local_28 = param_2;
  local_20 = param_1;
  puVar1 = __niter_base<unsigned_char*>(param_3);
  puVar2 = __niter_base<unsigned_char_const*>(local_28);
  puVar3 = __niter_base<unsigned_char_const*>(local_20);
  puVar1 = __copy_move_a1<false,unsigned_char_const*,unsigned_char*>(puVar3,puVar2,puVar1);
  puVar1 = __niter_wrap<unsigned_char*>(&local_30,puVar1);
  return puVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int const* std::__niter_base<int const*>(int const*)

int * std::__niter_base<int_const*>(int *param_1)

{
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::__niter_base<int*>(int*)

int * std::__niter_base<int*>(int *param_1)

{
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::__copy_move_a1<false, int const*, int*>(int const*, int const*, int*)

int * std::__copy_move_a1<false,int_const*,int*>(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  
  piVar1 = __copy_move_a2<false,int_const*,int*>(param_1,param_2,param_3);
  return piVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::__niter_wrap<int*>(int* const&, int*)

int * std::__niter_wrap<int*>(int **param_1,int *param_2)

{
  return param_2;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char const* std::__niter_base<unsigned char const*>(unsigned char const*)

uchar * std::__niter_base<unsigned_char_const*>(uchar *param_1)

{
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::__niter_base<unsigned char*>(unsigned char*)

uchar * std::__niter_base<unsigned_char*>(uchar *param_1)

{
  return param_1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::__copy_move_a1<false, unsigned char const*, unsigned char*>(unsigned char
// const*, unsigned char const*, unsigned char*)

uchar * std::__copy_move_a1<false,unsigned_char_const*,unsigned_char*>
                  (uchar *param_1,uchar *param_2,uchar *param_3)

{
  uchar *puVar1;
  
  puVar1 = __copy_move_a2<false,unsigned_char_const*,unsigned_char*>(param_1,param_2,param_3);
  return puVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::__niter_wrap<unsigned char*>(unsigned char* const&, unsigned char*)

uchar * std::__niter_wrap<unsigned_char*>(uchar **param_1,uchar *param_2)

{
  return param_2;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// int* std::__copy_move_a2<false, int const*, int*>(int const*, int const*, int*)

int * std::__copy_move_a2<false,int_const*,int*>(int *param_1,int *param_2,int *param_3)

{
  int *piVar1;
  
  piVar1 = __copy_move<false,true,std::random_access_iterator_tag>::__copy_m<int>
                     (param_1,param_2,param_3);
  return piVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// unsigned char* std::__copy_move_a2<false, unsigned char const*, unsigned char*>(unsigned char
// const*, unsigned char const*, unsigned char*)

uchar * std::__copy_move_a2<false,unsigned_char_const*,unsigned_char*>
                  (uchar *param_1,uchar *param_2,uchar *param_3)

{
  uchar *puVar1;
  
  puVar1 = __copy_move<false,true,std::random_access_iterator_tag>::__copy_m<unsigned_char>
                     (param_1,param_2,param_3);
  return puVar1;
}



// int* std::__copy_move<false, true, std::random_access_iterator_tag>::__copy_m<int>(int const*,
// int const*, int*)

int * std::__copy_move<false,true,std::random_access_iterator_tag>::__copy_m<int>
                (int *param_1,int *param_2,int *param_3)

{
  long lVar1;
  
  lVar1 = (long)param_2 - (long)param_1 >> 2;
  if (lVar1 != 0) {
    memmove(param_3,param_1,lVar1 * 4);
  }
  return param_3 + lVar1;
}



// unsigned char* std::__copy_move<false, true, std::random_access_iterator_tag>::__copy_m<unsigned
// char>(unsigned char const*, unsigned char const*, unsigned char*)

uchar * std::__copy_move<false,true,std::random_access_iterator_tag>::__copy_m<unsigned_char>
                  (uchar *param_1,uchar *param_2,uchar *param_3)

{
  size_t __n;
  
  __n = (long)param_2 - (long)param_1;
  if (__n != 0) {
    memmove(param_3,param_1,__n);
  }
  return param_3 + __n;
}



// std::vector<int, std::allocator<int> >::~vector()

void __thiscall std::vector<int,std::allocator<int>>::~vector(vector<int,std::allocator<int>> *this)

{
  allocator *paVar1;
  
  paVar1 = (allocator *)_Vector_base<int,std::allocator<int>>::_M_get_Tp_allocator();
  _Destroy<int*,int>(*(int **)this,*(int **)(this + 8),paVar1);
  _Vector_base<int,std::allocator<int>>::~_Vector_base
            ((_Vector_base<int,std::allocator<int>> *)this);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// void std::_Destroy<int*, int>(int*, int*, std::allocator<int>&)

void std::_Destroy<int*,int>(int *param_1,int *param_2,allocator *param_3)

{
  _Destroy<int*>(param_1,param_2);
  return;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked
// void std::_Destroy<int*>(int*, int*)

void std::_Destroy<int*>(int *param_1,int *param_2)

{
  _Destroy_aux<true>::__destroy<int*>(param_1,param_2);
  return;
}



// void std::_Destroy_aux<true>::__destroy<int*>(int*, int*)

void std::_Destroy_aux<true>::__destroy<int*>(int *param_1,int *param_2)

{
  return;
}



void __do_global_ctors_aux(void)

{
  code *pcVar1;
  undefined8 *puVar2;
  
  if (__CTOR_LIST__ != (code *)0xffffffffffffffff) {
    puVar2 = &__CTOR_LIST__;
    pcVar1 = __CTOR_LIST__;
    do {
      (*pcVar1)();
      pcVar1 = (code *)puVar2[-1];
      puVar2 = puVar2 + -1;
    } while (pcVar1 != (code *)0xffffffffffffffff);
    return;
  }
  return;
}



void _fini(void)

{
  __do_global_dtors_aux();
  return;
}


