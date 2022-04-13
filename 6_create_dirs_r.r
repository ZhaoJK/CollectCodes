# Load dir environments for single cells 
# Create or import path 


library(here)
library(fs)
root_dir <- here()
dataset_dir <- path_dir(root_dir)
raw_dir <- path_join(c(root_dir, "raw_data"))
raw_dir_join <-function(filename) {
    path_join(c(raw_dir,filename))
}   
data_dir <- path_join(c(root_dir, "data"))
data_dir_join <-function(filename) {
    path_join(c(data_dir,filename))
}   
if(!dir_exists(data_dir)) dir_create(data_dir)

table_dir <- path_join(c(root_dir, "tables"))
table_dir_join <-function(filename) {
    path_join(c(table_dir,filename))
} 
if(!dir_exists(table_dir)) dir_create(table_dir)

fig_dir <- path_join(c(root_dir, "figures"))
fig_dir_join <-function(filename) {
    path_join(c(fig_dir,filename))
} 
if(!dir_exists(fig_dir)) dir_create(fig_dir)

print(paste0("Directory to raw data: ", raw_dir))
print(paste0("Directory to data dir: ", data_dir))
print(paste0("Directory to talbe dir: ", table_dir))
print(paste0("Directory to figure dir: ", fig_dir))
