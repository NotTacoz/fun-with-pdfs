#!/usr/bin/env python3
""" pdfbook2 - transform pdf files to booklets
                   
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """


import os
import shutil
import subprocess
import sys
from optparse import HelpFormatter, OptionGroup, OptionParser

# ===============================================================================
# Create booklet for file $name
# ===============================================================================


def booklify(name, opts):
    # ------------------------------------------------------ Check if file exists
    print("\nProcessing", name)
    if not os.path.isfile(name):
        print("SKIP: file not found.")
        return
    print("Getting bounds...", end=" ")
    sys.stdout.flush()

    # ---------------------------------------------------------- useful constants
    bboxName = b"%%HiResBoundingBox:"
    tmpFile = ".crop-tmp.pdf"

    # ------------------------------------------------- find min/max bounding box
    if opts.crop:
        p = subprocess.Popen(
            ["pdfcrop", "--verbose", "--resolution", repr(opts.resolution), name, tmpFile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if len(err) != 0:
            print(err)
            print("\n\nABORT: Problem getting bounds")
            sys.exit(1)
        lines = out.splitlines()
        bboxes = [s[len(bboxName) + 1 :] for s in lines if s.startswith(bboxName)]
        bounds = [[float(x) for x in bbox.split()] for bbox in bboxes]
        minLOdd = min([bound[0] for bound in bounds[::2]])
        maxROdd = max([bound[2] for bound in bounds[::2]])
        if len(bboxes) > 1:
            minLEven = min([bound[0] for bound in bounds[1::2]])
            maxREven = max([bound[2] for bound in bounds[1::2]])
        else:
            minLEven = minLOdd
            maxREven = maxROdd
        minT = min([bound[1] for bound in bounds])
        maxB = max([bound[3] for bound in bounds])

        widthOdd = maxROdd - minLOdd
        widthEven = maxREven - minLEven
        maxWidth = max(widthOdd, widthEven)
        minLOdd -= maxWidth - widthOdd
        maxREven += maxWidth - widthEven

        print("done")
        sys.stdout.flush()

        # --------------------------------------------- crop file to area of interest
        print("cropping...", end=" ")
        sys.stdout.flush()
        p = subprocess.Popen(
            [
                "pdfcrop",
                "--bbox-odd",
                "{L} {T} {R} {B}".format(
                    L=minLOdd - opts.innerMargin / 2,
                    T=minT - opts.topMargin,
                    R=maxROdd + opts.outerMargin,
                    B=maxB + opts.outerMargin,
                ),
                "--bbox-even",
                "{L} {T} {R} {B}".format(
                    L=minLEven - opts.outerMargin,
                    T=minT - opts.topMargin,
                    R=maxREven + opts.innerMargin / 2,
                    B=maxB + opts.outerMargin,
                ),
                "--resolution",
                repr(opts.resolution),
                name,
                tmpFile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if len(err) != 0:
            print(err)
            print("\n\nABORT: Problem with cropping")
            sys.exit(1)
        print("done")
        sys.stdout.flush()
    else:
        shutil.copy(name, tmpFile)

    # -------------------------------------------------------- create the booklet
    print("create booklet...", end=" ")
    sys.stdout.flush()
    pdfJamCallList = [
        "pdfjam",
        "--landscape",
        "--suffix",
        "book",
        tmpFile,
    ]

    # add option signature if it is defined else booklet
    if opts.signature != 0:
        pdfJamCallList.append("--signature")
        pdfJamCallList.append(repr(opts.signature))
    else:
        pdfJamCallList.append("--booklet")
        pdfJamCallList.append("true")

    # add option --paper to call
    if opts.paper is not None:
        pdfJamCallList.append("--paper")
        pdfJamCallList.append(opts.paper)

    # add option --short-edge to call
    if opts.shortedge:
        # check if everyshi.sty exists as texlive recommends
        p = subprocess.Popen(
            ["kpsewhich", "everyshi.sty"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        if len(out) == 0:
            print("\n\nABORT: The everyshi.sty latex package is needed for short-edge.")
            sys.exit(1)
        else:
            pdfJamCallList.append("--preamble")
            pdfJamCallList.append(
                r"\usepackage{everyshi}\makeatletter\EveryShipout{\ifodd\c@page\pdfpageattr{/Rotate 180}\fi}\makeatother"
            )

    # run call to pdfJam to make booklet
    p = subprocess.Popen(pdfJamCallList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    # -------------------------------------------- move file and remove temp file
    os.rename(tmpFile[:-4] + "-book.pdf", name[:-4] + "-book.pdf")
    os.remove(tmpFile)
    print("done")
    sys.stdout.flush()


# ===============================================================================
# Help formatter
# ===============================================================================


class MyHelpFormatter(HelpFormatter):
    """Format help with indented section bodies.
    """

    def __init__(self, indent_increment=4, max_help_position=16, width=None, short_first=0):
        HelpFormatter.__init__(self, indent_increment, max_help_position, width, short_first)

    def format_usage(self, usage):
        return ("USAGE\n\n%*s%s\n") % (self.indent_increment, "", usage)

    def format_heading(self, heading):
        return "%*s%s\n\n" % (self.current_indent, "", heading.upper())


# ===============================================================================
# main programm
# ===============================================================================

if __name__ == "__main__":
    # ------------------------------------------------------------ useful strings
    usageString = "Usage: %prog [options] file1 [file2 ...]"
    versionString = """
    %prog v1.4 (https://github.com/jenom/pdfbook2)
    (c) 2015 - 2020 Johannes Neumann (http://www.neumannjo.de)
    licensed under GPLv3 (http://www.gnu.org/licenses/gpl-3.0)
    based on pdfbook by David Firth with help from Marco Pessotto\n"""
    defaultString = " (default: %default)"

    # ------------------------------------------------- create commandline parser
    parser = OptionParser(
        usage=usageString, version=versionString, formatter=MyHelpFormatter(indent_increment=4)
    )

    generalGroup = OptionGroup(parser, "General")
    generalGroup.add_option(
        "-p",
        "--paper",
        dest="paper",
        type="str",
        action="store",
        metavar="STR",
        help="Format of the output paper dimensions as latex keyword (e.g. a4paper, letterpaper, legalpaper, ...)",
    )
    generalGroup.add_option(
        "-s",
        "--short-edge",
        dest="shortedge",
        action="store_true",
        help="Format the booklet for short-edge double-sided printing",
        default=False,
    )
    generalGroup.add_option(
        "-n",
        "--no-crop",
        dest="crop",
        action="store_false",
        help="Prevent the cropping to the content area",
        default=True,
    )
    parser.add_option_group(generalGroup)

    marginGroup = OptionGroup(parser, "Margins")
    marginGroup.add_option(
        "-o",
        "--outer-margin",
        type="int",
        default=40,
        dest="outerMargin",
        action="store",
        metavar="INT",
        help="Defines the outer margin in the booklet" + defaultString,
    )
    marginGroup.add_option(
        "-i",
        "--inner-margin",
        type="int",
        default=150,
        dest="innerMargin",
        action="store",
        metavar="INT",
        help="Defines the inner margin between the pages in the booklet" + defaultString,
    )
    marginGroup.add_option(
        "-t",
        "--top-margin",
        type="int",
        default=30,
        dest="topMargin",
        action="store",
        metavar="INT",
        help="Defines the top margin in the booklet" + defaultString,
    )
    marginGroup.add_option(
        "-b",
        "--bottom-margin",
        type="int",
        default=30,
        metavar="INT",
        dest="bottomMargin",
        action="store",
        help="Defines the bottom margin in the booklet" + defaultString,
    )
    parser.add_option_group(marginGroup)

    advancedGroup = OptionGroup(parser, "Advanced")
    advancedGroup.add_option(
        "--signature",
        dest="signature",
        action="store",
        type="int",
        help="Define the signature for the booklet handed to pdfjam, needs to be multiple of 4"
        + defaultString,
        default=0,
        metavar="INT",
    )
    advancedGroup.add_option(
        "--signature*",
        dest="signature",
        action="store",
        type="int",
        help="Same as --signature",
        metavar="INT",
    )
    advancedGroup.add_option(
        "--resolution",
        dest="resolution",
        action="store",
        type="int",
        help="Resolution used by ghostscript in bp" + defaultString,
        metavar="INT",
        default=72,
    )
    parser.add_option_group(advancedGroup)

    opts, args = parser.parse_args()

    # ------------------------------------ show help if started without arguments
    if len(args) == 0:
        parser.print_version()
        parser.print_help()
        print("")
        sys.exit(2)

    # ------------------------------------------- run for each provided file name
    parser.print_version()
    for arg in args:
        booklify(arg, opts)