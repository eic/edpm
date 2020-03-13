"""
1  du -sch .[!.]* * |sort -h
    2  rm -rf .ccache pi400k.dat .cache
    3  ls
    4  cd -
    5  pwd
    6  exit
    7  source env.sh
    8  ejpm
    9  ejpm install ejana
   10  ls
   11  source env.sh
   12  ejpm install ejana
   13  which cmake
   14   ldd
   15  ldd cmake
   16  which cmake
   17  ldd /apps/cmake/cmake-3.13.4/bin/cmake
   18  ls /lib64/libz.so.1
   19  ls /lib64/
   20  ldd /apps/cmake/cmake-3.13.4/bin/cmake
   21  ejpm install ejana
   22  ldd /apps/cmake/cmake-3.13.4/bin/cmake
   23  ldd /lib64/libcrypto.so.10
   24  ls /lib64/libssl.so.10
   25  which openssl
   26  ldd /usr/local/lib64
   27  ldd /usr/bin/openssl
   28  cat /etc/ld.so.conf
   29  ejpm install root
   30  ejpm config root branch=v6-18-02
   31  ejpm install root
   32  ls
   33  micro
   34  ~/.cshrc
   35  vim ~/.cshrc
   36  micro ~/.cshrc
   37  echo $0
   38  ls
   39  cd ..
   40  micro
   41  cd -
   42  cd
   43  cd /work/eic/epic/
   44  ls
   45  vim cenv.csh
   46  micro cenv.csh
   47  source cenv.csh
   48  micro cenv.csh
   49  ls
   50  cd /work/eic/epic/
   51  ls
   52  source cenv.csh
   53  cp cenv.csh env.sh
   54  vim env.sh
   55  micro env.sh
   56  micro env.sh
   57  micro env.sh
   58  modules help
   59  modules
   60  nvim
   61  ls
   62  gedit
   63  gedit env.sh
   64  source env.sh
   65  gedit env.sh
   66  ls $EPIC_TOP_DIR/miniconda/etc/profile.d/
   67  gedit env.sh&>/dev/null
   68  source env.sh
   69  ejpm
   70  ejpm --top-dir=$EPIC_TOP_DIR
   71  mkdir /work/eic/epic/.ejpm_data
   72  ejpm --top-dir=$EPIC_TOP_DIR
   73  ejpm set root $EPIC_TOP_DIR/miniconda
   74  ejpm set geant $EPIC_TOP_DIR/miniconda
   75  ejpm install clhep
   76  conda install -c conda-forge cmake
   77  ejpm install clhep
   78  ejpm
   79  ejpm install vgm
   80  locate libEGL.so
   81  ls
   /envs/epic/bin/../x86_64-conda_cos6-linux-gnu/
   82  ls /work/eic/epic/miniconda/envs/epic/bin/../x86_64-conda_cos6-linux-gnu/sysroot/
   83  ls /work/eic/epic/miniconda/envs/epic/bin/../x86_64-conda_cos6-linux-gnu/sysroot/usr/
   84  ls /work/eic/epic/miniconda/envs/epic/bin/../x86_64-conda_cos6-linux-gnu/sysroot/usr/lib/*EGL.so
   85  ls /work/eic/epic/miniconda/envs/epic/bin/../x86_64-conda_cos6-linux-gnu/sysroot/usr/lib/
   86  sed -i 's|_qt5gui_find_extra_libs(EGL.*)|_qt5gui_find_extra_libs(EGL "EGL" "" "")|g' $PREFIX/lib/cmake/Qt5Gui/Qt5GuiConfigExtras.cmake
   87  conda update --all
   88  cd miniconda/
   89  ls
   90  ll
   91  ls -latrh
   92  cat .condarc
   93  conda config -h
   94  conda config --show
   95  ls
   96  ls ..
   97  ls ../conda_cache/
   98  conda update --all
   99  ejpm rm clhep
  100  conda
  101  conda install clhep
  102  conda install -c conda-forge clhep
  103  ejpm set clhep /work/eic/epic/miniconda/
  104  conda update -n base -c defaults condawork/eic/epic/miniconda/envs/epic/bin/
  105  conda update --all
  106  ejpm
  107  ejpm install vgm
  108  gedit fix_qt.sh&
  109  env|grep EPIC
  110  ls
  111  chmod +x fix_qt.sh
  112  ./fix_qt.sh
  113  ./fix_qt.sh
  114  ls  /work/eic/epic/miniconda/
  115  ls  /work/eic/epic/miniconda/lib/
  116  ls  /work/eic/epic/miniconda/envs/
  117  ls  /work/eic/epic/miniconda/envs/epic/
  118  conda info
  119  ./fix_qt.sh
  120  ejpm install vgm
  121  gedit "/work/eic/epic/miniconda/envs/epic/lib/cmake/Qt5Gui/Qt5GuiConfigExtras.cmake"
  122  conda install mesa-libGL
  123  conda install -c anaconda mesa-libgl-devel-cos6-x86_64
  124  ejpm install vgm
  125  ls /home/conda/feedstock_root/build_artifacts/geant4_1566302287089/_build_env/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64/libGL.so
  126  ls /home/conda/feedstock_root/build_artifacts/geant4_1566302287089/_build_env/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64/
  127  ls /home/conda/feedstock_root/build_artifacts/geant4_1566302287089/_build_env/x86_64-conda_cos6-linux-gnu/sysroot/usr/
  128  ls /home/conda/feedstock_root/build_artifacts/geant4_1566302287089/_build_env/
  129  ls /home/conda/feedstock_root/build_artifacts/geant4_1566302287089/
  130  ls /home/conda/feedstock_root/build_artifacts/
  131  ls /home/conda/feedstock_root/
  132  ldd packages/Geant4GM/libGeant4GM.so
  133  ldd envs/epic/packages/Geant4GM/libGeant4GM.so
  134  ldd envs/epic/lib/packages/Geant4GM/libGeant4GM.so
  135  locate Geant4GM
  136  ls
  137  cd ..
  138  ls
  139  cd vgm/
  140  ls
  141  cd src/
  142  ls
  143  cd v4-5/
  144  ls
  145  cd packages/
  146  ls
  147  cd Geant4GM/
  148  ls
  149  vim CMakeLists.txt
  150  ejpm install vgm
  151  rm -rf /work/eic/epic/vgm/build/v4-5
  152  ejpm install vgm
  153  vim CMakeLists.txt
  154  ejpm install vgm
  155  cd /work/eic/epic/miniconda/envs/epic/bin/../lib/Geant4-10.5.1
  156  ls
  157  cd Linux-g++/
  158  ls
  159  ls
  160  ldd libG4OpenGL.so
  161  ldd libG4geometry.so
  162  clear
  163  ldd libG4geometry.so
  164  ejpm install vgm
  165  conda --help
  166  conda remove geant4
  167  ejpm install geant
  168  ejpm rm geant
  169  ejpm install geant
  170  conda install xerces-c
  171  history
  172  ejpm install geant
  173  rm -rf /work/eic/epic/geant/build/v10.5.1
  174  ejpm install geant
  175  conda
  176  conda  list
  177  conda search xerces
  178  conda install xerces-c
  179  conda info xerces-c
  180  conda install -c conda-forge xerces-c
  181  ejpm install geant
  182  ls
  183  tmux ls
  184  tmux new
  185  tmux ls
  186  ps -aef | fgrep -i tmux
  187  tmux attach
  188  lsof -p 40883
  189  lsof -p 40570
  190  kill -s USR1 40570
  191  ls
  192  ps -aef | fgrep -i tmux
  193  tmux ls
  194  ps aux | grep -w [t]mux
  195  ls
  196  cd /work/eic/epic/
  197  ls
  198  echo $0
  199  source env.sh
  200  ls
  201  ejpm install g4e
  202  conda install -c conda-forge xorg-libxm
  203  conda install -c conda-forge xorg-libxmu
  204  history
  205  ls
  206  cd /work/eic/epic/
  207  ls
  208  ды
  209  las
  210  ls
  211  source env.sh
  212  ls
  213  ejpm
  214  ejpm install vgm
  215  ls
  216  ejpm
  217  ls
  218  source /work/eic/epic/.ejpm_data/env.sh
  219  ls /work/eic/epic/.ejpm_data/env.sh
  220  source /work/eic/epic/.ejpm_data/env.sh
  221  micro /work/eic/epic/.ejpm_data/env.sh
  222  source /work/eic/epic/.ejpm_data/env.sh
  223  ejpm install vgm
  224  rm -rf /work/eic/epic/vgm
  225  ejpm install vgm
  226  ls
  227  cd /work/eic/epic/vgm/build/v4-5
  228  micro cmake/FindCLHEP.cmake
  229  cd ..
  230  ls
  231  cd ..
  232  ls
  233  cd src/
  234  ls
  235  cd v4-5/
  236  ls
  237  micro cmake/FindCLHEP.cmake
  238  ejpm
  239  ls /work/eic/epic/miniconda
  240  ls /work/eic/epic/miniconda/lib/*hep*
  241  ls /work/eic/epic/miniconda/lib/*hep
  242  ls /work/eic/epic/miniconda/lib/
  243  ls /work/eic/epic/miniconda/
  244  ls /work/eic/epic/miniconda/envs/
  245  ls /work/eic/epic/miniconda/envs/epic/
  246  ls /work/eic/epic/miniconda/envs/epic/bin
  247  ls /work/eic/epic/miniconda/envs/epic
  248  ejpm
  249  ejpm help rm
  250  ejpm rm --help
  251  ejpm rm --db root /work/eic/epic/miniconda
  252  ejpm rm --db clhep /work/eic/epic/miniconda
  253  ejpm set root /work/eic/epic/miniconda/envs/epic
  254  ejpm set clhep /work/eic/epic/miniconda/envs/epic
  255  ejpm
  256  ejpm install vgm
  257  gcc --version
  258  conda install qt
  259  ejpm install vgm
  260  locate libglapi
  261  ldd /w/general-scifs17exp/eic/epic/miniconda/envs/epic/bin/../x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64/libGL.so
  262  ls /lib64/libglapi.so.0
  263  ll /lib64/libglapi.so.0
  264  conda install mesa-dri-drivers-cos6-x86_64
  265  ejpm install vgm
  266  ls \mnt\c\eic\g4e\work
  267  cd /work/eic/mc
  268  ll
  269  cd BEAGLE/
  270  ls
  271  cd GCF_SRC/
  272  ls
  273  cat GCF_boosted.txt
  274  less GCF_boosted.txt
  275  ll
  276  cd ..
  277  ll
  278  less eD_5x50_Q2_1_10_y_0.01_0.95_tau_7_noquench_kt=ptfrag=0.32_Shd1_ShdFac=1.32_Jpsidifflept_test40k_fixpf.txt
  279  less eD_5x50_Q2_1_10_y_0.01_0.95_tau_7_noquench_kt=ptfrag=0.32_Shd1_ShdFac=1.32_Jpsidifflept_test40k_fixpf_crang.txt
  280  ls
  281  cd ccdb/
  282  ls
  283  cd ccdb/
  284  ls
  285  cd
  286  ls
  287  cd rcdb/
  288  ls
  289  cat mk_tmp_rcdb_dump
  290  cd
  291  ls
  292  mysqldump -u ccdb -h hallddb --lock-tables=false --single-transaction ccdb | gzip -c | cat > 2019-11-30_ccdb.mysql.sql.gz
  293  mysqldump -u ccdb_user -h hallddb --lock-tables=false --single-transaction ccdb | gzip -c | cat > 2019-11-30_ccdb.mysql.sql.gz
  294  ls
  295  ls
  296  cd
  297  cat
  298  ls
  299  cat q
  300  cat ~bashrc
  301  exit
  302  ls
  303  cd rcdb/
  304  ls
  305  cd github_rcdb/
  306  git pull
  307  cd ..
  308  ls
  309  ./mk_clas12_rcdb_dump
  310  ls
  311  mv tmp_clas_rcdb.sql.gz clas_rcdb_2020-01-17.sql.gz
  312  ./mk_tmp_rcdb_dump
  313  ls
  314  mv tmp_rcdb.sql.gz halld_rcdb_2020-01-17.sql.gz
  315  ls
  316  ./copy_rcdb_www_to_halldweb
  317  ls
  318  docker
  319  sinfo
  320  singularity
  321  cd /group/eic/
  322  ls
  323  cd mc
  324  lsd
  325  ls
  326  cd BEAGLE/
  327  ls
  328  cd ..
  329  cd PYTHIA_6.5/
  330  ls
  331  ls
  332  cd DIS/
  333  ls
  334  cat pythia_e-p_10x100_Q10_100k_msel2_DIS.log
  335  cd
  336  cd -
  337  ls
  338  cd ..
  339  cd ..
  340  ls
  341  firefox&
  342  chromium&
  343  ssh yuliapc
  344  ssh -X yuliapc
  345  cd /scratch/romanov/mc
  346  cd /scratch/romanov/
  347  ls
  348  pwd
  349  cd /u//scratch/romanov/
  350  ls
  351  cd mc/
  352  ls
  353  cd pythia
  354  cd pythia8219/
  355  ls
  356  cd examples/
  357  ls
  358  make
  359  make main34
  360  ls
  361  cd ..
  362  ls
  363  cd bin/
  364  ls
  365  cat pythia8-config
  366  cd ..
  367  ls
  368  cd ..
  369  ls
  370  cd pythiaeRHIC/
  371  ls
  372  cd 1.0.0/
  373  ls
  374  cat HOW_TO_CONFIG
  375  ls
  376  make
  377  make clean
  378  cd ..
  379  ls
  380  cd 1.0.0/
  381  ls
  382  ls Ma*
  383  cd pythia/
  384  ls
  385  cd ..
  386  ls
  387  cd work/
  388  ls
  389  cd ..
  390  ls
  391  root
  392  ejpm
  393  ./configure
  394  make
  395  source /apps/root/6.18.04/bin/thisroot.sh
  396  ls
  397  ./configure
  398  ls
  399  ls -latrh
  400  cat README
  401  cd pythia/
  402  ls
  403  cd ..
  404  ls
  405  make install
  406  make
  407  ./configure
  408  make clean
  409  ./configure
  410  MAKE
  411  make
  412  cd ..
  413  ls
  414  cd ..
  415  ls
  416  cd Herwig6_HepMC/
  417  ls
  418  make
  419  make clean
  420  ls
  421  ./herwig6hepmc.sh
  422  ll DATA
  423  pwd
  424  ssh yuliapc
  425  ejpm
  426  cd /group/eic/epic/
  427  ls
  428  history


"""