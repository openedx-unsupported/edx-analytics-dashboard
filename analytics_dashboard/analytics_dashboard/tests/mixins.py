from waffle import Switch


class FeatureTestCaseMixin(object):
    def assertElementBehindFeature(self, url, selector, feature_name):
        # No interface with feature not created
        response = self.client.get(url)
        self.assertNotIn(selector, response.content)

        # Create the feature
        switch = Switch.objects.create(name=feature_name, active=False)

        # No interface with feature disabled
        response = self.client.get(url)
        self.assertNotIn(selector, response.content)

        # Interface should be present with feature enabled
        switch.active = True
        switch.save()
        response = self.client.get(url)
        self.assertIn(selector, response.content)
