from .configurations import TestBaseParameters, Urls


class TestContent(TestBaseParameters):
    def test_object_list(self):

        response = self.author_client.get(Urls.NOTES_LIST)

        object_list = response.context['object_list']

        self.assertIn(self.note, object_list)

    def test_note_creation_page_has_form(self):
        response = self.author_client.get(Urls.NOTE_ADD)

        self.assertContains(response, '<form', count=1)

    def test_note_edit_page_has_form(self):
        response = self.author_client.get(Urls.NOTE_EDIT)

        self.assertContains(response, '<form', count=1)

    def test_note_list_1_and_note_list_2_have_no_intersection(self):
        response_1 = self.author_client.get(Urls.NOTES_LIST)
        response_2 = self.author_client.get(Urls.NOTES_LIST)

        object_set_1 = set(response_1.context['object_list'])
        object_set_2 = set(response_2.context['object_list'])

        self.assertNotIn(object_set_1.intersection(object_set_2), object_set_2)
