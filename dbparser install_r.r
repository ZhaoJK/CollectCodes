BiocManager::install('OmnipathR')

install.packages("odbc")
install.packages("RMariaDB")
packageurl <- "https://cran.r-project.org/src/contrib/Archive/dbparser/dbparser_1.0.4.tar.gz"
install.packages(packageurl, repos=NULL, type="source")

