"""Сериалайзеры."""

import base64
import datetime as dt

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Achievement, AchievementCat, Cat


class Hex2NameColor(serializers.Field):
    """Поле сериализатора для конвертации HEX-кода цвета в название."""

    def to_representation(self, value):
        """Возвращает значение цвета."""
        return value

    def to_internal_value(self, data):
        """Конвертирует HEX-код в название цвета."""
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AchievementSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Achievement с полем имени."""

    achievement_name = serializers.CharField(source='name')

    class Meta:
        """Метаданные для AchievementSerializer."""

        model = Achievement
        fields = ('id', 'achievement_name')


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображения в формате base64."""

    def to_internal_value(self, data):
        """Преобразует base64-данные в объект изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CatSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Cat с достижениями, цветом и возрастом."""

    achievements = AchievementSerializer(required=False, many=True)
    color = Hex2NameColor()
    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        """Метаданные для CatSerializer."""

        model = Cat
        fields = (
            'id', 'name', 'color', 'birth_year', 'achievements',
            'owner', 'age', 'image', 'image_url'
        )
        read_only_fields = ('owner',)

    def get_image_url(self, obj):
        """Возвращает URL изображения, если оно есть."""
        if obj.image:
            return obj.image.url
        return None

    def get_age(self, obj):
        """Вычисляет возраст на основе года рождения."""
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        """Создаёт экземпляр Cat с достижениями, если они указаны."""
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        achievements = validated_data.pop('achievements')
        cat = Cat.objects.create(**validated_data)
        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement
            )
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat
            )
        return cat

    def update(self, instance, validated_data):
        """Обновляет экземпляр Cat, включая достижения."""
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.birth_year = validated_data.get(
            'birth_year', instance.birth_year
        )
        instance.image = validated_data.get('image', instance.image)

        if 'achievements' not in validated_data:
            instance.save()
            return instance

        achievements_data = validated_data.pop('achievements')
        lst = []
        for achievement in achievements_data:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement
            )
            lst.append(current_achievement)
        instance.achievements.set(lst)

        instance.save()
        return instance
