/**
 * Lumebook creator signup form (Hebrew), built 2026-10-03.
 *
 * How to run:
 *   1. Go to https://script.google.com → New project
 *   2. Delete the sample code, paste this whole file, Save
 *   3. Pick createLumebookCreatorForm in the toolbar → Run → approve the Google permissions
 *   4. Open View → Logs (Execution log) for the form link + edit link
 *
 * Creates: the form + a linked responses Sheet in your Drive.
 * It tries to move both into the shared "שיווק" folder; if that fails they stay in My Drive.
 */

const MARKETING_FOLDER_ID = '1awITcQFWfsQqpbL8Lupikw12b6y4EWvB'; // Drive "שיווק"
const LIVE_FORM_ID = '1Iupo4um1A65aWE_-paWCpbeOeD3ZkIKYhPxN-T_NtS8'; // form built 2026-10-03

const SOCIAL_TITLE = 'אינסטגרם / טיקטוק';
const SOCIAL_HELP = 'שם משתמש או קישור לפרופיל (אפשר את שניהם)';
const MILESTONE_TITLE = 'מה מתקרב אצלכם בחודשים הקרובים?';
const EMAIL_TITLE = 'מייל';
const FOLLOWERS_TITLE = 'כמה עוקבים יש לכם?';
const FOLLOWERS_CHOICES = ['פחות מ-1,000', '1,000 ומעלה'];

function addEmailItem(form) {
  return form.addTextItem()
    .setTitle(EMAIL_TITLE)
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .requireTextIsEmail()
      .setHelpText('נא להזין כתובת מייל תקינה')
      .build());
}

function addFollowersItem(form) {
  return form.addMultipleChoiceItem()
    .setTitle(FOLLOWERS_TITLE)
    .setHelpText('בחשבון הגדול מביניהם')
    .setChoiceValues(FOLLOWERS_CHOICES)
    .setRequired(true);
}

function addMilestoneItem(form) {
  return form.addCheckboxItem()
    .setTitle(MILESTONE_TITLE)
    .setHelpText('לא חובה, עוזר לנו להתאים לכם ספר')
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
}

/**
 * One-off edit of the live form (2026-10-03): merge Instagram + TikTok, add the milestone question.
 * Safe to re-run: skips steps that are already done.
 */
function updateLumebookCreatorForm() {
  const form = FormApp.openById(LIVE_FORM_ID);
  const find = title => form.getItems().find(i => i.getTitle() === title);

  const ig = find('אינסטגרם');
  if (ig) ig.asTextItem().setTitle(SOCIAL_TITLE).setHelpText(SOCIAL_HELP);
  const tiktok = find('טיקטוק');
  if (tiktok) form.deleteItem(tiktok);

  if (!find(MILESTONE_TITLE)) {
    const milestone = addMilestoneItem(form);
    form.moveItem(milestone.getIndex(), find('אישור').getIndex());
  }

  Logger.log(form.getItems().map(i => i.getTitle()).join(' | '));
}

/**
 * Second edit of the live form (2026-10-03): drop kids' ages, add email + follower band.
 * Safe to re-run.
 */
function updateLumebookCreatorFormV2() {
  const form = FormApp.openById(LIVE_FORM_ID);
  const find = title => form.getItems().find(i => i.getTitle() === title);

  const ages = find('גילאי הילדים');
  if (ages) form.deleteItem(ages);

  if (!find(EMAIL_TITLE)) {
    const email = addEmailItem(form);
    form.moveItem(email.getIndex(), find('מספר וואטסאפ').getIndex() + 1);
  }
  if (!find(FOLLOWERS_TITLE)) {
    const followers = addFollowersItem(form);
    form.moveItem(followers.getIndex(), find(SOCIAL_TITLE).getIndex() + 1);
  }

  Logger.log(form.getItems().map(i => i.getTitle()).join(' | '));
}

function createLumebookCreatorForm() {
  const form = FormApp.create('יוצרי תוכן × לומבוק');

  form.setDescription([
    'מצלמים את הילדים ומשתפים? בואו ליצור איתנו.',
    'בלומבוק הילדים שלכם הופכים לגיבורי הסיפור: ספר מאויר עם הפנים והשם שלהם.',
    '',
    'מה מקבלים:',
    '• ספר מותאם אישית במתנה',
    '• קוד הנחה אישי לעוקבים שלכם',
    '• 20% עמלה על כל הזמנה דרך הקוד',
    '• שיתוף התוכן שלכם ב-@lumebookai',
    '',
    'מה מבקשים:',
    '• רילס / טיקטוק של הרגע שהילדים פוגשים את עצמם בספר',
    '• תיוג @lumebookai וסימון שיתוף פעולה',
    '',
    'ממלאים פה, ואם יש התאמה, נחזור אליכם בוואטסאפ',
  ].join('\n'));

  form.setConfirmationMessage('תודה! קיבלנו 💛 אם יש התאמה נחזור אליכם בוואטסאפ');
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setShowLinkToRespondAgain(false);

  // 1. Name
  form.addTextItem()
    .setTitle('שם מלא')
    .setRequired(true);

  // 2. WhatsApp
  form.addTextItem()
    .setTitle('מספר וואטסאפ')
    .setHelpText('לשם נחזור אליכם')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation()
      .requireTextMatchesPattern('^[0-9+\\-\\s()]{9,16}$')
      .setHelpText('נא להזין מספר טלפון, למשל 050-1234567')
      .build());

  // 3. Email
  addEmailItem(form);

  // 4. Instagram / TikTok + follower band
  form.addTextItem()
    .setTitle(SOCIAL_TITLE)
    .setHelpText(SOCIAL_HELP)
    .setRequired(true);
  addFollowersItem(form);

  // 5. Upcoming milestone (optional)
  addMilestoneItem(form);

  // 6. Combined consent
  form.addCheckboxItem()
    .setTitle('אישור')
    .setHelpText([
      '• אני מעל גיל 18 וההורה או האפוטרופוס של הילדים שמופיעים בתוכן',
      '• לומבוק יכולה לשתף את התוכן בערוצים שלה, עם קרדיט',
      '• התוכן יסומן כשיתוף פעולה (למשל "קיבלתי במתנה") ויתויג @lumebookai',
      '• שימוש בתוכן בפרסום ממומן: רק באישור נפרד',
      '• אפשר לבקש הסרה בכל שלב בוואטסאפ',
    ].join('\n'))
    .setChoiceValues(['מאשרים'])
    .setRequired(true);

  // Responses → new Sheet
  const sheet = SpreadsheetApp.create('יוצרי תוכן × לומבוק (תגובות)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  // Move into the shared marketing folder if we can
  try {
    const folder = DriveApp.getFolderById(MARKETING_FOLDER_ID);
    DriveApp.getFileById(form.getId()).moveTo(folder);
    DriveApp.getFileById(sheet.getId()).moveTo(folder);
    Logger.log('Moved form + sheet into the שיווק folder');
  } catch (e) {
    Logger.log('Could not move into the שיווק folder (left in My Drive): ' + e);
  }

  Logger.log('Form link (share this): ' + form.getPublishedUrl());
  Logger.log('Edit link: ' + form.getEditUrl());
  Logger.log('Responses sheet: ' + sheet.getUrl());
}
