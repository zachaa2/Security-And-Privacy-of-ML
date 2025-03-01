@echo off
FOR %%s IN (1314 11314 21314 31314 41314 51314 61314 71314) DO (
    SET CUDA_VISIBLE_DEVICES=0
    python -u ./src/gmixup.py --data_path . --model GIN --dataset REDDIT-BINARY ^
        --lr 0.01 --gmixup True --seed=%%s  --log_screen True --batch_size 128 --num_hidden 64 ^
        --aug_ratio 0.15 --aug_num 10  --ge USVT
)
