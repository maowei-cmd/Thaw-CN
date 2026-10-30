//
//  ThawBarSupplementTests.swift
//  Project: Thaw
//
//  Copyright (Thaw) © 2026 Toni Förster
//  Licensed under the GNU GPLv3

import MenuBarModel
import Testing
@testable import Thaw

@Suite("Thaw Bar supplement")
struct ThawBarSupplementTests {
    private func item(_ identifier: String) -> MenuBarItem {
        MenuBarItem(
            tag: MenuBarItemTag(namespace: .string("test.\(identifier)"), title: identifier),
            windowID: 1,
            ownerPID: 1,
            sourcePID: 1,
            bounds: CGRect(x: 0, y: 0, width: 20, height: 20),
            title: identifier,
            isOnScreen: true
        )
    }

    @Test("Supplement items follow the section items")
    func appendsSupplement() {
        let merged = ThawBarSupplement.merged(
            sectionItems: [item("hidden")],
            supplement: [item("missing")]
        )
        #expect(merged.map(\.title) == ["hidden", "missing"])
    }

    @Test("A supplement item already in the section is not duplicated")
    func dropsDuplicates() {
        let same = item("same")
        let merged = ThawBarSupplement.merged(sectionItems: [same], supplement: [same])
        #expect(merged.map(\.uniqueIdentifier) == [same.uniqueIdentifier])
    }

    @Test("No supplement leaves the section alone")
    func emptySupplement() {
        let section = [item("a"), item("b")]
        #expect(ThawBarSupplement.merged(sectionItems: section, supplement: []).map(\.uniqueIdentifier) == section.map(\.uniqueIdentifier))
    }
}
