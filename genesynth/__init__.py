
#!/usr/bin/env python
from genesynth.cli import main, parser

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.filename, args.output)
