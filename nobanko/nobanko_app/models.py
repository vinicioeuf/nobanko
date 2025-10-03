from django.conf import settings
from django.db import models


class Usuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    cpf = models.CharField(max_length=14, unique=True)
    birth_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "Perfil do usuário"
        verbose_name_plural = "Perfis dos usuários"

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.get_username()