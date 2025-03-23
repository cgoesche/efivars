#!/usr/bin/python3 -I
'''
What:           efivars
Description:    List EFI variables made available in RAM from the UEFI NV-RAM

                The list of variables is divided into two sections, the first being the UEFI
                defined variables as described in the UEFI Specification v2.11
                (https://uefi.org/sites/default/files/resources/UEFI_Spec_Final_2.11.pdf),
                and the second section contains all vendor specific variables defined by the
                vendors UEFI firmware.
Author:         Christian Goeschel Ndjomouo <cgoesc2@wgu.edu>
Date:           Mar 22 2025
'''

import os
import re
import sys

# Global variables
UEFI_GLOBAL_VARIABLE_GUID = "8be4df61-93ca-11d2-aa0d-00e098032b8c"
SYSFS_EFIVARSFS = "/sys/firmware/efi/efivars"

# Technically speaking UEFI variables stored in the NV-RAM are not
# directly accessible from the OS level. They are rather made residents
# of RAM by the UEFI firmware at boot time for exposure to the 'efivarfs'
# interface driver which will make them available in /sys/firmware/efi/efivars
# hence why we will enumerate all files in the latter.
def enum_efi_vars(efivarsfs_path: str = SYSFS_EFIVARSFS) -> list:
    """
    Enumerates UEFI variables exposed in SYSFS_EFIVARSFS.

    Args:
        efivarsfs_path (str): Absolute filesystem path to efivarsfs ,default (SYSFS_EFIVARSFS)

    Returns:
            list: All found variables in SYSFS_EFIVARSFS
    """
    efi_vars = []
    for (dirpath, dirnames, filenames) in os.walk(efivarsfs_path):
        efi_vars.extend(filenames)
        break

    return efi_vars

# Here we will sort the enumerated EFI variables into two distinct lists.
def sort_efi_vars(efi_vars_list: list, uefi_global_vars_guid: str) -> tuple:
    """
    Sorts the enumerated EFI variables into two different lists.
    'uefi_spec_vars' will contain variables defined by the UEFI Specification
    and 'vendor_spec_vars' will be vendor defined variables

    Args:
        list (efi_vars_list):           An unsorted list of EFI variables
        str (uefi_global_vars_guid):    UEFI global variables guid for the regex pattern

    Returns:
            tuple (uefi_spec_vars, vendor_spec_vars):  List of UEFI and vendor specific variables, respectively
    """
    uefi_spec_vars =            []
    vendor_spec_vars =          []
    # As defined in UEFI Specification v2.11 8.2.3 variables have to be minimum 1 char long
    uefi_vars_regex_pattern =   re.compile(f"^.+-{uefi_global_vars_guid}$")

    for var in efi_vars_list:
        if not uefi_vars_regex_pattern.match(var):
            vendor_spec_vars.append(var)
        else:
            uefi_spec_vars.append(var)

    return uefi_spec_vars, vendor_spec_vars

# Pretty print a list
def print_list(l: list, l_name: str) -> None:
    l_size = len(l)

    print("{} {}\n".format(l_size, l_name))
    for e in l:
        print(e)


# Entrypoint
def main() -> None:
    # Testing if the 'efivarfs' at /sys/firmware/efi/efivars has been created
    try:
        os.stat(SYSFS_EFIVARSFS)
    except Exception as e:
        print("""
        {}\n
        EFI variables can not be listed on your system

        Please make sure your kernel isn't booted with the 'noefi' parameter and is configured
        with 'CONFIG_EFI=y', otherwise run the command below as root and try again.

        mount -t efivarfs efivarfs /sys/firmware/efi/efivars""".format(e))
        sys.exit(2)

    all_efi_vars = enum_efi_vars(SYSFS_EFIVARSFS)

    if not all_efi_vars:
        print("Something seems wrong, no EFI variables found!")
        sys.exit(3)

    uefi_spec_vars, vendor_spec_vars = sort_efi_vars(all_efi_vars, UEFI_GLOBAL_VARIABLE_GUID)
    print_list(uefi_spec_vars, "[UEFI Specification v2.11 defined EFI variables]")
    print("")
    print_list(vendor_spec_vars, "[Vendor defined EFI variables]")

# Enter the entrypoint only if this script is ran directly
if __name__ == '__main__':
    main()