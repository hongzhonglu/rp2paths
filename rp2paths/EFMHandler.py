"""Find pathways from Elementary Flux Modes enumeration.

Copyright (C) 2016-2017 Thomas Duigou, JL Faulon's research group, INRA

Use of this source code is governed by the MIT license that can be found in the
LICENSE.txt file.

"""

import os
import argparse
import csv
from .pyEMSv2.elemodes import Elemodes


class EFMHandler(object):
    """Handling result generated by the EFM enumeration tool."""

    def __init__(self,
                 full_react_file, react_file, efm_file,
                 outfile='out_paths.csv',
                 unfold_stoichio=False, unfold_compounds=False,
                 maxsteps=15, maxpaths=150):
        """Initialization."""
        # .
        self.full_react_file = full_react_file
        self.react_file = react_file
        self.efm_file = efm_file
        self.outfile = outfile
        self.unfold_stoichio = unfold_stoichio
        self.unfold_compounds = unfold_compounds
        self.maxsteps = maxsteps
        self.maxpaths = maxpaths
        self.elemodes = None

    def _CheckArgs(self):
        """Perform some checking on arguments."""
        assert type(self.unfold_stoichio) is bool
        assert type(self.unfold_compounds) is bool
        assert type(self.maxsteps) is int and self.maxsteps > 0
        assert type(self.maxpaths) is int and self.maxpaths >= 0
        for filepath in (self.full_react_file, self.react_file, self.efm_file):
            if not os.path.exists(filepath):
                raise IOError(filepath)

    def ParseEFMs(self):
        """Parse raw EFM results."""
        self.elemodes = Elemodes(react_name_file=self.react_file,
                                 full_react_file=self.full_react_file,
                                 efm_file=self.efm_file,
                                 maxsteps=self.maxsteps)

    def WriteCsv(self):
        """Unfold (if necessary) and write results."""
        # Prepare output file
        fields = ['Path ID', 'Unique ID', 'Rule ID', 'Left', 'Right']
        fh = open(self.outfile, 'w')
        writer = csv.DictWriter(fh, fieldnames=fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        # Get pathways from enumeration results
        pathways = self.elemodes.GetPathways(
            unfold_stoichio=self.unfold_stoichio,
            unfold_compounds=self.unfold_compounds,
            maxsteps=self.maxsteps)
        # Write
        pid = 0
        for path in pathways:
            pid += 1
            # Stop enumerating if we reach the allowed max number of pathways
            if pid > self.maxpaths:
                fh.close()
                return
            for rxn in path:
                writer.writerow(
                    {'Path ID': pid,
                     'Unique ID': rxn.name,
                     'Rule ID': rxn.enzyme,
                     'Left': ':'.join([str(c) for c in rxn.subs]),
                     'Right': ':'.join([str(c) for c in rxn.prods])
                     })
        fh.close()

    def compute(self):
        """Do it."""
        self._CheckArgs()
        self.ParseEFMs()
        self.WriteCsv()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find pathways from \
                                     Elementary Flux Modes enumeration')
    parser.add_argument('--indir', required=True,
                        help='Folder containing the enumeration to parse.')
    parser.add_argument('--source', required=True,
                        help='ID of the source compound.')
    parser.add_argument('--basename', default='out',
                        help='Basename of files generated by the enumeration.')
    parser.add_argument('--outfile',
                        help='Output file.')
    parser.add_argument('--unfold_stoichio', default=False,
                        action='store_true',
                        help='Unfold pathways based on the stoichiometry \
                        matrix (can lead to combinatorial explosion).')
    parser.add_argument('--unfold_compounds', default=False,
                        action='store_true',
                        help='Unfold pathways based on equivalencie of \
                        compounds (can lead to combinatorial explosion).')
    parser.add_argument('--maxsteps', default=10, type=int,
                        help='Cutoff on the maximum number of steps in a \
                        pathways.')
    parser.add_argument('--maxpaths', default=150, type=int,
                        help='cutoff on the maximum number of pathways.')
    # Get arguments
    args = parser.parse_args()

    # Compute
    full_react_file = os.path.join(args.indir, args.basename + '_full_react')
    react_file = os.path.join(args.indir, args.basename + '_react')
    efm_file = os.path.join(args.indir, args.basename + '_efm')

    p = EFMHandler(
        full_react_file=full_react_file,
        react_file=react_file,
        efm_file=efm_file,
        outfile=args.outfile,
        unfold_stoichio=args.unfold_stoichio,
        unfold_compounds=args.unfold_compounds,
        maxsteps=args.maxsteps, maxpaths=args.maxpaths)
    p.compute()