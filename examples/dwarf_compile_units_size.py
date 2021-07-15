#-------------------------------------------------------------------------------
# elftools example: dwarf_compile_units_size.py <binary>
#
# Examine DW_TAG_compile_unit DIE entries which have range list values,
# and compute the total size of ranges.
#
# Mauro Passerino (mauropasse2@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from __future__ import print_function
import sys

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.common.py3compat import itervalues
from elftools.elf.elffile import ELFFile
from elftools.dwarf.descriptions import (
    describe_DWARF_expr, set_global_machine_arch)
from elftools.dwarf.ranges import RangeEntry


def process_file(filename):
    print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()

        # The range lists are extracted by DWARFInfo from the .debug_ranges
        # section, and returned here as a RangeLists object.
        range_lists = dwarfinfo.range_lists()
        if range_lists is None:
            print('  file has no .debug_ranges section')
            return

        for CU in dwarfinfo.iter_CUs():
            # DWARFInfo allows to iterate over the compile units contained in
            # the .debug_info section. CU is a CompileUnit object, with some
            # computed attributes (such as its offset in the section) and
            # a header which conforms to the DWARF standard. The access to
            # header elements is, as usual, via item-lookup.
            # A CU provides a simple API to iterate over all the DIEs in it.
            for DIE in CU.iter_DIEs():
                # Go over all attributes of the DIE. Each attribute is an
                # AttributeValue object (from elftools.dwarf.die), which we
                # can examine.
                if DIE.tag == "DW_TAG_compile_unit":
                    for attr in itervalues(DIE.attributes):
                        if attr.name == 'DW_AT_ranges':
                            # This is a range list. Its value is an offset into
                            # the .debug_ranges section, so we can use the range
                            # lists object to decode it.
                            rangelist = range_lists.get_range_size_at_offset(attr.value)

                            top_DIE = CU.get_top_DIE()
                            cu = top_DIE.get_full_path()
                            print("%s %s" % (cu, rangelist))


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        process_file(filename)
