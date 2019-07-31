/**
 * Created by apple on 2018/11/29.
 */
var touchTarget,
    touchScreenX,
    touchScreenY,
    conditionParentUntilTrue,
    disableScroll;

conditionParentUntilTrue = function (element, condition) {
    var outcome;

    if (element === document.body) {
        return false;
    }

    outcome = condition(element);

    if (outcome) {
        return true;
    } else {
        return conditionParentUntilTrue(element.parentNode, condition);
    }
};

window.addEventListener('touchstart', function (e) {
    touchTarget = e.targetTouches[0].target;
    scrollMap = {}

    scrollMap.left = conditionParentUntilTrue(touchTarget, function (element) {
        return element.scrollLeft > 0;
    });

    scrollMap.top = conditionParentUntilTrue(touchTarget, function (element) {
        return element.scrollTop > 0;
    });

    scrollMap.right = conditionParentUntilTrue(touchTarget, function (element) {
        return element.scrollWidth > element.clientWidth &&
               element.scrollWidth - element.clientWidth > element.scrollLeft;
    });

    scrollMap.bottom =conditionParentUntilTrue(touchTarget, function (element) {
        return element.scrollHeight > element.clientHeight &&
               element.scrollHeight - element.clientHeight > element.scrollTop;
    });

    touchScreenX = e.targetTouches[0].screenX;
    touchScreenY = e.targetTouches[0].screenY;
    disableScroll = false;
});

window.addEventListener('touchmove', function (e) {
    var moveScreenX,
        moveScreenY;

    if (disableScroll) {
        e.preventDefault();
        return;
    }

    moveScreenX = e.targetTouches[0].screenX;
    moveScreenY = e.targetTouches[0].screenY;

    if (
        moveScreenX > touchScreenX && scrollMap.left ||
        moveScreenY < touchScreenY && scrollMap.bottom ||
        moveScreenX < touchScreenX && scrollMap.right ||
        moveScreenY > touchScreenY && scrollMap.top
    ) {
    } else {
        e.preventDefault();
        disableScroll = true;
    }
});