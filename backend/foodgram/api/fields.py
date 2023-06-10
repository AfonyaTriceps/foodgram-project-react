import webcolors
from rest_framework import serializers


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            for color in data:
                color = webcolors.hex_to_name(color)
        except ValueError:
            raise serializers.ValidationError('Такого цвета нет')
        return data
