//
//  ThawBarSupplement.swift
//  Project: Thaw
//
//  Copyright (Thaw) © 2026 Toni Förster
//  Licensed under the GNU GPLv3

import MenuBarModel

/// Items added to the Thaw Bar because macOS does not draw them on this
/// display's own bar. They follow the section's items and never duplicate one.
enum ThawBarSupplement {
    static func merged(sectionItems: [MenuBarItem], supplement: [MenuBarItem]) -> [MenuBarItem] {
        let existing = Set(sectionItems.map(\.uniqueIdentifier))
        return sectionItems + supplement.filter { !existing.contains($0.uniqueIdentifier) }
    }
}
