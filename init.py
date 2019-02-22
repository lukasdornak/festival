# -*- coding: utf-8 -*-
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from festival import models

sections = [{
    'role' : 'b',
    'order' : 1,
    'headline' : 'o festivalu',
    'headline_en' : 'about festival',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;o festivalu&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;about fest&quot; section for visitors.</p>',
},{
    'role' : 'b',
    'order' : 2,
    'headline' : 'hot news',
    'headline_en' : 'hot news',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;hot news&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;hot news&quot; section for visitors.</p>',
},{
    'role' : 'b',
    'order' : 3,
    'headline' : 'galerie',
    'headline_en' : 'gallery',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;galerie&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;gallery&quot; section for visitors.</p>',
},{
    'role' : 'b',
    'order' : 4,
    'headline' : 'doprava',
    'headline_en' : 'traffic',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;doprava&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;traffic&quot; section for visitors.</p>',
},{
    'role' : 'b',
    'order' : 5,
    'headline' : 'ubytování',
    'headline_en' : 'accomodation',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;ubytování&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;accomodation&quot; section for visitors.</p>',
},{
    'role' : 'b',
    'order' : 6,
    'headline' : 'partneři',
    'headline_en' : 'partners',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;partneři&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;partners&quot; section for visitors.</p>',
},{
    'role' : 'b',
    'order' : 7,
    'headline' : 'kontakty',
    'headline_en' : 'contacts',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;kontakty&quot; pro n&aacute;v&scaron;těvn&iacute;ky</p>',
    'full_text_en' : '<p>English content of &quot;contacts&quot; section for visitors.</p>',
},{
    'role' : 'a',
    'order' : 1,
    'headline' : 'o festivalu',
    'headline_en' : 'about festival',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;o festivalu&quot; pro tvůrce.</p>',
    'full_text_en' : '<p>English content of &quot;about fest&quot; section for authors.</p>',
},{
    'role' : 'a',
    'order' : 2,
    'headline' : 'doprava',
    'headline_en' : 'traffic',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;doprava&quot; pro tvůrce.</p>',
    'full_text_en' : '<p>English content of &quot;traffic&quot; section for authors.</p>',
},{
    'role' : 'a',
    'order' : 3,
    'headline' : 'ubytování',
    'headline_en' : 'accomodation',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;ubytování&quot; pro tvůrce.</p>',
    'full_text_en' : '<p>English content of &quot;accomodation&quot; section for authors.</p>',
},{
    'role' : 'a',
    'order' : 4,
    'headline' : 'partneři',
    'headline_en' : 'partners',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;partneři&quot; pro tvůrce.</p>',
    'full_text_en' : '<p>English content of &quot;partners&quot; section for authors.</p>',
},{
    'role' : 'a',
    'order' : 5,
    'headline' : 'kontakty',
    'headline_en' : 'contacts',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;kontakty&quot; pro tvůrce.</p>',
    'full_text_en' : '<p>English content of &quot;contacts&quot; section for authors.</p>',
},{
    'role' : 'c',
    'order' : 1,
    'headline' : 'o festivalu',
    'headline_en' : 'about festival',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;o festivalu&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;about fest&quot; section for journalists.</p>',
},{
    'role' : 'c',
    'order' : 2,
    'headline' : 'tiskovky',
    'headline_en' : 'press releases',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;tiskovky&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;press releases&quot; section for journalists.</p>',
},{
    'role' : 'c',
    'order' : 3,
    'headline' : 'loga',
    'headline_en' : 'logos',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;loga&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;logos&quot; section for journalists.</p>',
},{
    'role' : 'c',
    'order' : 4,
    'headline' : 'galerie',
    'headline_en' : 'gallery',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;galerie&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;gallery&quot; section for journalists.</p>',
},{
    'role' : 'c',
    'order' : 5,
    'headline' : 'doprava',
    'headline_en' : 'traffic',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;doprava&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;traffic&quot; section for journalists.</p>',
},{
    'role' : 'c',
    'order' : 6,
    'headline' : 'partneři',
    'headline_en' : 'partners',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;partneři&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;partners&quot; section for journalists.</p>',
},{
    'role' : 'c',
    'order' : 7,
    'headline' : 'kontakty',
    'headline_en' : 'contacts',
    'full_text' : '<p>Česk&yacute; obsah sekce &quot;kontakty&quot; pro novin&aacute;ře.</p>',
    'full_text_en' : '<p>English content of &quot;contacts&quot; section for journalists.</p>',
}]

if not models.Section.objects.all().exists():
    for s in sections:
        print(s['headline'])
        models.Section(role=s['role'], order=s['order'], headline=s['headline'], headline_en=s['headline_en'],
                       full_text=s['full_text'], full_text_en=s['full_text_en']).save()
