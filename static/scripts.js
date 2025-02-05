function convertPersianDigitToEnglish(id) {
    var persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    var englishDigits = '0123456789';
    let persianString = $(id).val()

    for (var i = 0; i < persianDigits.length; i++) {
        var regex = new RegExp(persianDigits[i], 'g');
        persianString = persianString.replace(regex, englishDigits[i]);
    }

    $(id).val(persianString)
}