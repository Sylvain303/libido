#!/bin/bash
# 
# Usage: ./make_it.sh
#
# simulate libido behavior with the current syntaxe
# Will recreate $dst 

src=readme_ex0.sh
dst=readme_ex0.result.sh

# extract code of die() from $lib
lib="libido/shell_lib.bash"
match=$(python ../python/bash_parser.py $lib | sed -n -e '/^die: / { s/// ; s/,/;/; p }')

# extracted position in the lib, will define $start and $end
echo $match
eval $match

# initilize the $dst with top file content
line_expand=$(sed -n -e '/libido: expand bash_code/ =' $src)
sed -n -e "1,$line_expand p" $src > $dst

# replace expand call with EXPANDED marker
sed -i -e "$line_expand c\
# libido: expand bash_code => EXPANDED {
" $dst

# extract the code and append it to $dst
echo "start=${start} end=${end}"
cmd="sed -n -e '$start,$end p'"
eval $cmd $lib >> $dst

# add end block marker
echo '# libido: => EXPANDED }' >> $dst

# append final code
sed -n -e"$(($line_expand + 1)),\$ p" $src >> $dst

# add expanded REF in the header
sed -i -e '/libido: bash_code=/ a\
# libido: => REF(libido/shell_lib.bash)
' $dst

diff -u $src $dst
# last one should output nothing identical readme_ex0.result.sh expected
diff -q readme_ex0.result0.sh readme_ex0.result.sh 
