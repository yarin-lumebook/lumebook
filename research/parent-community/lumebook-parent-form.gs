/**
 * LumeBook parent sign-up form (Hebrew): shooting day for social media, for a free personalised book.
 * Written 2026-10-15. Separate from the creator form (creators/lumebook-ugc-form.gs).
 *
 * How to run:
 *   1. Go to https://script.google.com → New project
 *   2. Delete the sample code, paste this whole file, Save
 *   3. Pick createLumebookParentForm in the toolbar → Run → approve the Google permissions
 *   4. Open View → Logs (Execution log) for the form link, edit link and Sheet link
 *   5. Put the form link in the posts instead of [קישור לטופס]
 *
 * Creates: the form + a linked responses Sheet in your Drive.
 * It tries to move both into the shared "שיווק" folder; if that fails they stay in My Drive.
 * The form collects children's names and ages, so keep the Sheet private (do not share the link).
 */

const MARKETING_FOLDER_ID = '1awITcQFWfsQqpbL8Lupikw12b6y4EWvB'; // Drive "שיווק"

function createLumebookParentForm() {
  const form = FormApp.create('יום צילום עם לומיבוק: הרשמה למשפחות');
  form.setDescription(
    'לומיבוק מכינים ספרי ילדים מותאמים אישית שבהם הילד הוא הגיבור.\n' +
    'אנחנו מחפשים כמה משפחות עם ילדים בגילאי 1 עד 10 ליום צילום קצר אצלכם בבית לרשתות החברתיות של לומיבוק.\n' +
    'מצלמים את הילד ואת ההורה עם הספר, והספר נשאר אצלכם במתנה. זו כל התמורה.\n' +
    'מתחילים באשקלון והסביבה. לא כל הפניות ייבחרו, ונחזור אליכם בוואטסאפ.\n\n' +
    'בבקשה לא לשלוח כאן תמונות של ילדים.')
    .setCollectEmail(false)
    .setAllowResponseEdits(false)
    .setLimitOneResponsePerUser(false)
    .setShowLinkToRespondAgain(false)
    .setConfirmationMessage('תודה! קיבלנו את הפרטים. אם נבחר אתכם, נחזור אליכם בוואטסאפ.');

  // About the parent
  form.addSectionHeaderItem().setTitle('פרטי ההורה');
  form.addTextItem().setTitle('שם מלא').setRequired(true);
  form.addTextItem()
    .setTitle('טלפון (וואטסאפ)')
    .setHelpText('כאן נחזור אליכם')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .requireTextMatchesPattern('^[0-9+\\-\\s]{9,15}$')
      .setHelpText('נא להזין מספר טלפון תקין')
      .build());
  form.addMultipleChoiceItem()
    .setTitle('אני')
    .setChoiceValues(['אמא', 'אבא', 'אפוטרופוס/ית חוקי/ת'])
    .setRequired(true);
  form.addTextItem().setTitle('עיר או ישוב').setRequired(true);
  form.addTextItem()
    .setTitle('שכונה')
    .setHelpText('לא חובה. עוזר לנו לתכנן מסלול')
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle('אפשר להגיע אליכם בתחבורה ציבורית?')
    .setHelpText('אנחנו מגיעים בתחבורה ציבורית')
    .setChoiceValues(['כן', 'לא', 'לא בטוח/ה'])
    .setRequired(true);

  // About the child
  form.addSectionHeaderItem()
    .setTitle('פרטי הילד או הילדה')
    .setHelpText('הספר נכתב במיוחד בשביל הילד, לכן אנחנו צריכים את הפרטים האלה');
  form.addTextItem().setTitle('שם פרטי של הילד/ה').setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('בן או בת?')
    .setChoiceValues(['בן', 'בת'])
    .setRequired(true);
  form.addListItem()
    .setTitle('גיל')
    .setChoiceValues(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    .setRequired(true);
  form.addTextItem()
    .setTitle('עוד ילדים שיופיעו בסרטון? (שם וגיל)')
    .setHelpText('לא חובה. אפשר לכתוב אחים או אחיות שרוצים להצטלם')
    .setRequired(false);
  form.addCheckboxItem()
    .setTitle('מה מתקרב אצלכם בחודשים הקרובים?')
    .setHelpText('לא חובה, עוזר לנו להתאים את הספר')
    .setChoiceValues([
      "כניסה לגן / לכיתה א'",
      'אח/ות בדרך',
      'גמילה מטיטולים',
      'גמילה ממוצץ',
      'פחד או קושי (חושך, פרידה...)',
      'יום הולדת',
      'חג (חנוכה...)',
      'כלום מיוחד',
    ])
    .showOtherOption(true)
    .setRequired(false);

  // Scheduling
  form.addSectionHeaderItem().setTitle('מתי נוח לכם?');
  form.addCheckboxItem()
    .setTitle('ימים מתאימים')
    .setChoiceValues(['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי'])
    .setRequired(true);
  form.addCheckboxItem()
    .setTitle('שעות מתאימות')
    .setChoiceValues(['בוקר', 'צהריים', 'אחר הצהריים'])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('שפת הצילום והספר')
    .setChoiceValues(['עברית', 'רוסית', 'אנגלית', 'ערבית'])
    .setHelpText('עברית היא הבטוחה ביותר, בשאר השפות נבדוק מה אפשר')
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle('איפה שמעתם עלינו?')
    .setChoiceValues(['קבוצת פייסבוק', 'קבוצת וואטסאפ', 'אינסטגרם', 'חבר/ה', 'אחר'])
    .setRequired(false);
  form.addParagraphTextItem()
    .setTitle('משהו שחשוב לנו לדעת?')
    .setRequired(false);

  // Confirmations (all must be ticked)
  form.addSectionHeaderItem()
    .setTitle('לפני השליחה')
    .setHelpText('חובה לאשר את כל השורות');
  [
    'אני ההורה או האפוטרופוס החוקי של כל הילדים שיצטלמו',
    'אני מבין/ה שרואים בסרטונים בבירור את הפנים של הילד ושלי',
    'אני מבין/ה שהסרטונים יעלו לעמודים של לומיבוק ברשתות החברתיות',
    'אני מבין/ה שהספר במתנה הוא כל התמורה',
    'אני מבין/ה שלא כל הפניות ייבחרו, ושלפני הצילום אחתום על הסכמה בכתב',
  ].forEach(text => {
    form.addCheckboxItem()
      .setTitle(text)
      .setChoiceValues(['מאשר/ת'])
      .setRequired(true);
  });

  // Responses sheet
  const sheet = SpreadsheetApp.create('יום צילום עם לומיבוק: תגובות');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  try {
    const folder = DriveApp.getFolderById(MARKETING_FOLDER_ID);
    DriveApp.getFileById(form.getId()).moveTo(folder);
    DriveApp.getFileById(sheet.getId()).moveTo(folder);
  } catch (e) {
    Logger.log('Could not move into the שיווק folder, left in My Drive: ' + e);
  }

  Logger.log('FORM LINK (put this in the post): ' + form.getPublishedUrl());
  Logger.log('EDIT LINK: ' + form.getEditUrl());
  Logger.log('SHEET: ' + sheet.getUrl());
}
