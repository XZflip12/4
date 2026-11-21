# Сжатие изображений квадродеревом

Проект реализует вариант «Сжатие изображений» из `README.md`.

## Установка

```text
python -m pip install -r requirements.txt
```

## Запуск

```text
python -m image_compressor input.png -o compressed.png ^
  --boundaries tree.png --gif compression.gif ^
  --compression 60 --workers 4
```

`--compression` принимает значение от `0` (минимальная потеря качества) до
`100` (максимальное укрупнение однородных областей). Параметр `--workers`
включает обработку четырех верхних областей в потоках. Опции `--boundaries` и
`--gif` являются необязательными.

## Проверка

```text
python -m pytest -q
pylint image_compressor
```
