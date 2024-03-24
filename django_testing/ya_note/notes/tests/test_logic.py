from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note

from .configurations import TestBaseParameters, Urls


class TestLogic(TestBaseParameters):
    def test_anonymous_user_cant_create_note(self):
        initial_notes_count = Note.objects.count()

        response = self.client.post(Urls.NOTE_ADD, data=self.note_data)

        final_notes_count = Note.objects.count()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertEqual(initial_notes_count, final_notes_count)

    def test_auth_user_can_create_note(self):
        initial_notes_count = Note.objects.count()

        response = self.author_client.post(Urls.NOTE_ADD, data=self.note_data)

        final_notes_count = Note.objects.count()

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(initial_notes_count, final_notes_count)

    def test_author_can_edit_notes(self):
        self.assertRedirects(
            self.author_client.post(
                Urls.NOTE_EDIT, data=self.new_note_data
            ),
            Urls.NOTES_SUCCESS
        )

        note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(
            (note.title, note.text, note.slug, note.author),
            (self.new_note_data['title'], self.new_note_data['text'],
             self.new_note_data['slug'], self.author)
        )

    def test_reader_cant_edit_notes_of_another_user(self):
        response = self.reader_client.post(
            Urls.NOTE_EDIT, data=self.new_note_data
        )

        note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertNotEqual(
            (note.title, note.text, note.slug, note.author),
            (self.new_note_data['title'], self.new_note_data['text'],
             self.new_note_data['slug'], self.author)
        )

    def test_author_can_delete_notes(self):
        self.assertRedirects(
            self.author_client.post(Urls.NOTE_DELETE), Urls.NOTES_SUCCESS
        )

        notes_count = Note.objects.count()

        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_notes_of_another_user(self):
        response = self.reader_client.post(Urls.NOTE_DELETE)

        notes_count = Note.objects.count()

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(notes_count, 1)

    def test_anonymous_cant_delete_notes_of_another_user(self):
        response = self.client.post(Urls.NOTE_DELETE)

        notes_count = Note.objects.count()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertEqual(notes_count, 1)

    def test_unique_slug(self):
        note_2 = Note.objects.create(
            title=self.note_data['title'],
            text=self.note_data['text'],
            author=self.author
        )

        self.assertNotEqual(self.note.slug, note_2.slug)

    def test_auto_slug_generate(self):
        note = Note.objects.create(
            title=self.note_data['title'],
            text=self.note_data['text'],
            author=self.author
        )

        expected_slug = slugify(note.title)

        self.assertEqual(note.slug, expected_slug)
