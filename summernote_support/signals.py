from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from markets.models import Market
from products.models import Product
from qna.models import Question
from summernote_support.models import RelatedAttachment


@receiver(post_save, sender=Question)
def on_post_question_save(sender, instance: Question, created: bool, raw: bool, using, update_fields, **kwargs):
    new_attachments = instance.extract_attachments()
    related_attachments = instance.related_attachments.all()

    del_related_attachments = []
    create_related_attachments = []

    for related_attachment in related_attachments:
        need_to_delete = True

        for new_attachment in new_attachments:
            if related_attachment.attachment_id == new_attachment.id:
                need_to_delete = False
                break

        if need_to_delete:
            del_related_attachments.append(related_attachment)

    for new_attachment in new_attachments:
        need_to_create = True

        for related_attachment in related_attachments:
            if related_attachment.attachment_id == new_attachment.id:
                need_to_create = False
                break

        if need_to_create:
            create_related_attachments.append(new_attachment)

    for del_related_attachment in del_related_attachments:
        attachment = del_related_attachment.attachment
        del_related_attachment.delete()
        attachment.file.delete()
        attachment.delete()

    for create_related_attachment in create_related_attachments:
        RelatedAttachment.objects.create(content_type=ContentType.objects.get_for_model(instance), object_id=instance.id, attachment=create_related_attachment)
